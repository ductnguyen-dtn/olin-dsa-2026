"""The servo-movement math, ported tick-for-tick from C++.

Pipeline (one control tick, per servo)::

    joint angle [rad]
        │  joint_angle_to_proportional()      ← spot_micro_motion_cmd.cpp
        ▼      publishServoProportionalCommand()
    proportional command ∈ [-1, 1]
        │  proportional_to_pwm_counts()        ← i2cpwm_board, proportional mode
        ▼
    raw 12-bit PWM count ∈ [0, 4096]

``command_all_servos()`` runs the whole pipeline for the twelve-servo dict, the
same job ``setServoCommandMessageData()`` + ``publishServoProportionalCommand()``
do together in the original node.
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass

from spotmicro_servo.config import (
    DEFAULT_SERVO_CONFIG,
    PWM_COUNTS_FULL_SCALE,
    SERVO_MAX_ANGLE_DEG,
    ServoCalibration,
)


class ProportionalClipError(ValueError):
    """Raised in ``strict`` mode when a commanded angle lands outside the
    servo's travel and would have to be clipped.

    In the C++ node this case is not an error: it logs ``ROS_WARN`` and clamps
    to ±1.0.  The port keeps that as the default and offers ``strict=True`` for
    tests and callers that would rather fail loudly.
    """


@dataclass(frozen=True)
class ServoCommand:
    """Result of the full pipeline for one servo."""

    name: str
    servo_num: int
    proportional: float
    pwm_counts: int
    clipped: bool


def joint_angle_to_proportional(
    cmd_ang_rad: float,
    calibration: ServoCalibration,
    *,
    servo_max_angle_deg: float = SERVO_MAX_ANGLE_DEG,
    strict: bool = False,
) -> float:
    """Convert a commanded joint angle to a proportional command in ``[-1, 1]``.

    Direct port of the body of ``publishServoProportionalCommand()``::

        float center_ang_rad = servo_config_params["center_angle_deg"] * M_PI / 180.0f;
        float servo_proportional_cmd =
            (cmd_ang_rad - center_ang_rad) / (smnc_.servo_max_angle_deg * M_PI / 180.0f);
        if (servo_proportional_cmd > 1.0f)  servo_proportional_cmd = 1.0f;   // + ROS_WARN
        else if (servo_proportional_cmd < -1.0f) servo_proportional_cmd = -1.0f;

    Parameters
    ----------
    cmd_ang_rad:
        Commanded joint angle, radians, in the joint's own frame.
    calibration:
        Calibration for this servo (supplies ``center_angle_deg``).
    servo_max_angle_deg:
        Single-direction travel limit; the denominator of the scaling.
    strict:
        If ``True`` raise :class:`ProportionalClipError` instead of clipping.

    Returns
    -------
    float
        Proportional command, guaranteed to be within ``[-1.0, 1.0]``.
    """
    if servo_max_angle_deg <= 0:
        raise ValueError(
            f"servo_max_angle_deg must be positive, got {servo_max_angle_deg}"
        )

    center_ang_rad = math.radians(calibration.center_angle_deg)
    proportional = (cmd_ang_rad - center_ang_rad) / math.radians(servo_max_angle_deg)

    if -1.0 <= proportional <= 1.0:
        return proportional

    clipped_value = 1.0 if proportional > 1.0 else -1.0
    message = (
        f"proportional command {proportional:+.3f} outside [-1, 1] "
        f"(joint angle {math.degrees(cmd_ang_rad):.1f} deg); clipped to {clipped_value:+.1f}"
    )
    if strict:
        raise ProportionalClipError(message)
    warnings.warn(message, stacklevel=2)
    return clipped_value


def clamp_pwm_counts(counts: int) -> int:
    """Clamp a raw PWM count into the PCA9685's 12-bit range ``[0, 4096]``."""
    return max(0, min(PWM_COUNTS_FULL_SCALE, counts))


def proportional_to_pwm_counts(
    proportional: float,
    calibration: ServoCalibration,
) -> int:
    """Convert a proportional command to a raw 12-bit PWM count.

    Port of the ``i2cpwm_board`` "proportional" command path.  The board holds
    each servo's ``center`` and ``range`` (set once via the config service, the
    job of ``publishServoConfiguration()``), then for a proportional ``value``::

        pos = center + value * (range / 2) * direction        // then clamp to [0, 4096]

    ``range`` is the full end-to-end span, hence ``range / 2`` per side.
    """
    if not -1.0 <= proportional <= 1.0:
        raise ValueError(
            f"proportional command must be in [-1, 1], got {proportional}"
        )
    pos = calibration.center + proportional * (calibration.range / 2.0) * calibration.direction
    return clamp_pwm_counts(round(pos))


def zero_absolute_command(
    config: dict[str, ServoCalibration] | None = None,
) -> dict[int, int]:
    """Return an "all servos off" absolute command: every port set to 0 counts.

    Port of ``publishZeroServoAbsoluteCommand()`` — a 0-count pulse produces no
    signal, so the servos stop holding position and can be back-driven by hand.
    Keyed by PCA9685 port number.
    """
    config = DEFAULT_SERVO_CONFIG if config is None else config
    return {cal.num: 0 for cal in config.values()}


def command_all_servos(
    joint_angles_rad: dict[str, float],
    config: dict[str, ServoCalibration] | None = None,
    *,
    servo_max_angle_deg: float = SERVO_MAX_ANGLE_DEG,
    strict: bool = False,
) -> dict[str, ServoCommand]:
    """Run the full pipeline for every servo named in ``joint_angles_rad``.

    Mirrors one control tick: ``setServoCommandMessageData()`` copies the twelve
    joint angles into ``servo_cmds_rad_``, then ``publishServoProportionalCommand()``
    walks the config map and fills the outgoing servo array.

    Raises
    ------
    KeyError
        If an angle is given for a servo not in ``config``, or vice versa — the
        C++ maps are always populated in lockstep, so a mismatch is a bug.
    """
    config = DEFAULT_SERVO_CONFIG if config is None else config

    missing = set(config) - set(joint_angles_rad)
    extra = set(joint_angles_rad) - set(config)
    if missing or extra:
        raise KeyError(
            f"joint angle / config mismatch (missing={sorted(missing)}, "
            f"extra={sorted(extra)})"
        )

    commands: dict[str, ServoCommand] = {}
    for name, calibration in config.items():
        raw = (joint_angles_rad[name] - math.radians(calibration.center_angle_deg)) / math.radians(
            servo_max_angle_deg
        )
        proportional = joint_angle_to_proportional(
            joint_angles_rad[name],
            calibration,
            servo_max_angle_deg=servo_max_angle_deg,
            strict=strict,
        )
        commands[name] = ServoCommand(
            name=name,
            servo_num=calibration.num,
            proportional=proportional,
            pwm_counts=proportional_to_pwm_counts(proportional, calibration),
            clipped=not -1.0 <= raw <= 1.0,
        )
    return commands
