"""Per-servo calibration data.

C++ origin
----------
In ``spot_micro_motion_cmd`` the calibration lives in a nested ``std::map``::

    std::map<std::string, std::map<std::string, float>> servo_config;

populated from ``spot_micro_motion_cmd.yaml`` by ``readInConfigParameters()``.
Each inner map has the keys ``num``, ``center``, ``range``, ``direction`` and
``center_angle_deg``.  Here that inner map becomes a typed :class:`ServoCalibration`
dataclass so the field names are checked instead of being stringly-typed.
"""

from __future__ import annotations

from dataclasses import dataclass

#: ``servo_max_angle_deg`` from the YAML: the largest single-direction command
#: angle any servo will accept.  Slightly under 90 deg to stay off the mechanical
#: stops.  Global in the C++ config (``smnc_.servo_max_angle_deg``).
SERVO_MAX_ANGLE_DEG: float = 82.5

#: PWM board resolution.  The PCA9685 is a 12-bit device, so a pulse count is an
#: integer in ``[0, 4096]`` (0 = no pulse, 4096 = always high).
PWM_COUNTS_FULL_SCALE: int = 4096


@dataclass(frozen=True)
class ServoCalibration:
    """Calibration for one servo, matching one inner map in the C++ config.

    Attributes
    ----------
    num:
        PCA9685 port the servo is wired to, numbered 1-16.  Used as a 1-based
        index into the outgoing servo array (``servo_array_.servos[num - 1]``).
    center:
        Raw 12-bit PWM count that holds the servo at its mechanical centre
        (~1.5 ms pulse, about 306).
    range:
        Raw PWM-count span between the servo's two calibration extremes, i.e.
        counts at ``+servo_max_angle_deg`` minus counts at
        ``-servo_max_angle_deg``.
    direction:
        ``+1`` or ``-1``; flips the sign of servo rotation for joints whose
        positive-angle convention is opposite the servo's.
    center_angle_deg:
        Joint angle, in that joint's own coordinate frame, that corresponds to
        the servo sitting at ``center``.
    """

    num: int
    center: int
    range: int
    direction: int
    center_angle_deg: float

    def __post_init__(self) -> None:
        if self.direction not in (-1, 1):
            raise ValueError(f"direction must be +1 or -1, got {self.direction}")
        if not 1 <= self.num <= 16:
            raise ValueError(f"num must be in 1..16, got {self.num}")
        if self.range < 0:
            raise ValueError(f"range must be non-negative, got {self.range}")


#: Servo names in leg order.  "R"/"L" = right/left, "F"/"B" = front/back,
#: trailing 1/2/3 = hip / shoulder / knee joint.  Order matches the physical
#: wiring order documented in ``docs/servo_calibration.md``.
SERVO_NAMES: tuple[str, ...] = (
    "RF_1", "RF_2", "RF_3",
    "RB_1", "RB_2", "RB_3",
    "LB_1", "LB_2", "LB_3",
    "LF_1", "LF_2", "LF_3",
)

#: Default calibration, copied verbatim from ``spot_micro_motion_cmd.yaml``.
#: Every servo shares ``center = 306`` on this build; the ``range`` and
#: ``center_angle_deg`` values come from the calibration spreadsheet.
DEFAULT_SERVO_CONFIG: dict[str, ServoCalibration] = {
    "RF_3": ServoCalibration(num=1,  center=306, range=372, direction=1,  center_angle_deg=88.2),
    "RF_2": ServoCalibration(num=2,  center=306, range=389, direction=1,  center_angle_deg=-27.6),
    "RF_1": ServoCalibration(num=3,  center=306, range=396, direction=-1, center_angle_deg=-5.4),
    "RB_3": ServoCalibration(num=4,  center=306, range=396, direction=1,  center_angle_deg=85.8),
    "RB_2": ServoCalibration(num=5,  center=306, range=396, direction=1,  center_angle_deg=-35.4),
    "RB_1": ServoCalibration(num=6,  center=306, range=411, direction=1,  center_angle_deg=-4.4),
    "LB_3": ServoCalibration(num=7,  center=306, range=390, direction=1,  center_angle_deg=-73.9),
    "LB_2": ServoCalibration(num=8,  center=306, range=392, direction=1,  center_angle_deg=38.7),
    "LB_1": ServoCalibration(num=9,  center=306, range=374, direction=-1, center_angle_deg=-0.4),
    "LF_3": ServoCalibration(num=10, center=306, range=387, direction=1,  center_angle_deg=-82.8),
    "LF_2": ServoCalibration(num=11, center=306, range=397, direction=1,  center_angle_deg=38.6),
    "LF_1": ServoCalibration(num=12, center=306, range=389, direction=1,  center_angle_deg=-7.6),
}
