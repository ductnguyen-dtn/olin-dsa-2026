"""Python port of the Spot Micro servo-movement code.

Ported from the C++ node ``spot_micro_motion_cmd`` (file
``spot_micro_motion_cmd/src/spot_micro_motion_cmd.cpp``) and the downstream
``i2cpwm_board`` driver.  The original computes, every control tick, a
proportional command in ``[-1, 1]`` for each of the twelve leg servos from a
commanded joint angle and a per-servo calibration, then the PWM board converts
that proportional value into a raw 12-bit pulse count.

This package keeps that math and nothing else: no ROS, no I2C, no threads.
"""

from spotmicro_servo.config import (
    DEFAULT_SERVO_CONFIG,
    SERVO_MAX_ANGLE_DEG,
    SERVO_NAMES,
    ServoCalibration,
)
from spotmicro_servo.commands import (
    ProportionalClipError,
    clamp_pwm_counts,
    command_all_servos,
    joint_angle_to_proportional,
    proportional_to_pwm_counts,
    zero_absolute_command,
)

__all__ = [
    "DEFAULT_SERVO_CONFIG",
    "SERVO_MAX_ANGLE_DEG",
    "SERVO_NAMES",
    "ServoCalibration",
    "ProportionalClipError",
    "clamp_pwm_counts",
    "command_all_servos",
    "joint_angle_to_proportional",
    "proportional_to_pwm_counts",
    "zero_absolute_command",
]
