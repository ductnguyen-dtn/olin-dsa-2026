"""Tests for the Spot Micro servo-movement port.

Key properties carried over from the C++:
* centre angle -> proportional 0.0 -> PWM count == ``center``
* proportional is linear in angle and saturates (or raises) outside travel
* PWM counts never leave ``[0, 4096]``
* ``direction`` flips which way counts move
"""

from __future__ import annotations

import math

import pytest

from spotmicro_servo import (
    DEFAULT_SERVO_CONFIG,
    SERVO_MAX_ANGLE_DEG,
    SERVO_NAMES,
    ProportionalClipError,
    ServoCalibration,
    clamp_pwm_counts,
    command_all_servos,
    joint_angle_to_proportional,
    proportional_to_pwm_counts,
    zero_absolute_command,
)

# A simple, symmetric calibration for arithmetic that is easy to check by hand.
SIMPLE = ServoCalibration(num=1, center=306, range=400, direction=1, center_angle_deg=0.0)
SIMPLE_REVERSED = ServoCalibration(num=2, center=306, range=400, direction=-1, center_angle_deg=0.0)


# --------------------------------------------------------------------------- #
# joint_angle_to_proportional
# --------------------------------------------------------------------------- #

def test_center_angle_maps_to_zero() -> None:
    assert joint_angle_to_proportional(0.0, SIMPLE) == 0.0


def test_offset_center_angle_maps_to_zero() -> None:
    cal = ServoCalibration(num=1, center=306, range=400, direction=1, center_angle_deg=30.0)
    assert joint_angle_to_proportional(math.radians(30.0), cal) == pytest.approx(0.0)


def test_full_positive_travel_maps_to_plus_one() -> None:
    angle = math.radians(SERVO_MAX_ANGLE_DEG)
    assert joint_angle_to_proportional(angle, SIMPLE) == pytest.approx(1.0)


def test_full_negative_travel_maps_to_minus_one() -> None:
    angle = math.radians(-SERVO_MAX_ANGLE_DEG)
    assert joint_angle_to_proportional(angle, SIMPLE) == pytest.approx(-1.0)


def test_half_travel_maps_to_half() -> None:
    angle = math.radians(SERVO_MAX_ANGLE_DEG / 2.0)
    assert joint_angle_to_proportional(angle, SIMPLE) == pytest.approx(0.5)


def test_beyond_travel_clips_and_warns_by_default() -> None:
    angle = math.radians(SERVO_MAX_ANGLE_DEG + 20.0)
    with pytest.warns(UserWarning, match="clipped"):
        assert joint_angle_to_proportional(angle, SIMPLE) == 1.0


def test_beyond_travel_negative_clips_to_minus_one() -> None:
    angle = math.radians(-(SERVO_MAX_ANGLE_DEG + 5.0))
    with pytest.warns(UserWarning):
        assert joint_angle_to_proportional(angle, SIMPLE) == -1.0


def test_strict_mode_raises_instead_of_clipping() -> None:
    angle = math.radians(SERVO_MAX_ANGLE_DEG + 0.1)
    with pytest.raises(ProportionalClipError):
        joint_angle_to_proportional(angle, SIMPLE, strict=True)


def test_exact_endpoint_is_not_clipped() -> None:
    # +servo_max_angle_deg lands on exactly +1.0 and must not warn.
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert joint_angle_to_proportional(math.radians(SERVO_MAX_ANGLE_DEG), SIMPLE) == pytest.approx(1.0)


def test_zero_servo_max_angle_rejected() -> None:
    with pytest.raises(ValueError):
        joint_angle_to_proportional(0.0, SIMPLE, servo_max_angle_deg=0.0)


# --------------------------------------------------------------------------- #
# proportional_to_pwm_counts
# --------------------------------------------------------------------------- #

def test_proportional_zero_gives_center_counts() -> None:
    assert proportional_to_pwm_counts(0.0, SIMPLE) == 306


def test_proportional_plus_one_gives_center_plus_half_range() -> None:
    assert proportional_to_pwm_counts(1.0, SIMPLE) == 306 + 200


def test_proportional_minus_one_gives_center_minus_half_range() -> None:
    assert proportional_to_pwm_counts(-1.0, SIMPLE) == 306 - 200


def test_direction_reverses_offset() -> None:
    assert proportional_to_pwm_counts(1.0, SIMPLE_REVERSED) == 306 - 200
    assert proportional_to_pwm_counts(-1.0, SIMPLE_REVERSED) == 306 + 200


def test_counts_are_clamped_to_12_bit_range() -> None:
    huge = ServoCalibration(num=1, center=4000, range=4000, direction=1, center_angle_deg=0.0)
    assert proportional_to_pwm_counts(1.0, huge) == 4096
    low = ServoCalibration(num=1, center=50, range=4000, direction=1, center_angle_deg=0.0)
    assert proportional_to_pwm_counts(-1.0, low) == 0


def test_proportional_out_of_range_rejected() -> None:
    with pytest.raises(ValueError):
        proportional_to_pwm_counts(1.5, SIMPLE)


@pytest.mark.parametrize(
    "raw, expected", [(-10, 0), (0, 0), (306, 306), (4096, 4096), (5000, 4096)]
)
def test_clamp_pwm_counts(raw: int, expected: int) -> None:
    assert clamp_pwm_counts(raw) == expected


# --------------------------------------------------------------------------- #
# command_all_servos  (one full control tick)
# --------------------------------------------------------------------------- #

def test_all_servos_at_their_center_angles_command_center_counts() -> None:
    # Feed each servo exactly its center_angle_deg -> every proportional is 0.0
    # and every PWM count is the servo's center (306 on this build).
    angles = {
        name: math.radians(cal.center_angle_deg)
        for name, cal in DEFAULT_SERVO_CONFIG.items()
    }
    commands = command_all_servos(angles)
    assert set(commands) == set(DEFAULT_SERVO_CONFIG)
    for cmd in commands.values():
        assert cmd.proportional == pytest.approx(0.0)
        assert cmd.pwm_counts == 306
        assert cmd.clipped is False


def test_command_all_servos_reports_servo_num_and_clipping() -> None:
    angles = {name: math.radians(cal.center_angle_deg) for name, cal in DEFAULT_SERVO_CONFIG.items()}
    # Drive RF_1 way past its travel.
    angles["RF_1"] = math.radians(DEFAULT_SERVO_CONFIG["RF_1"].center_angle_deg + 200.0)
    with pytest.warns(UserWarning):
        commands = command_all_servos(angles)
    assert commands["RF_1"].clipped is True
    assert commands["RF_1"].servo_num == DEFAULT_SERVO_CONFIG["RF_1"].num
    assert abs(commands["RF_1"].proportional) == 1.0


def test_command_all_servos_rejects_mismatched_keys() -> None:
    with pytest.raises(KeyError):
        command_all_servos({"RF_1": 0.0})  # missing the other 11


def test_command_all_servos_rejects_unknown_servo() -> None:
    angles = {name: 0.0 for name in DEFAULT_SERVO_CONFIG}
    angles["NOPE_9"] = 0.0
    with pytest.raises(KeyError):
        command_all_servos(angles)


# --------------------------------------------------------------------------- #
# config sanity
# --------------------------------------------------------------------------- #

def test_default_config_has_twelve_unique_ports() -> None:
    assert len(DEFAULT_SERVO_CONFIG) == 12
    ports = sorted(cal.num for cal in DEFAULT_SERVO_CONFIG.values())
    assert ports == list(range(1, 13))


def test_default_config_names_match_servo_names_constant() -> None:
    assert set(DEFAULT_SERVO_CONFIG) == set(SERVO_NAMES)


def test_calibration_rejects_bad_direction() -> None:
    with pytest.raises(ValueError):
        ServoCalibration(num=1, center=306, range=400, direction=0, center_angle_deg=0.0)


def test_zero_absolute_command_is_all_ports_zero() -> None:
    off = zero_absolute_command()
    assert sorted(off) == list(range(1, 13))
    assert set(off.values()) == {0}
