# Porting: Spot Micro servo-movement code (C++ → typed Python)

## Purpose of the original code

The source is part of **Spot Micro**, an open-source quadruped robot that runs
on a Raspberry Pi. The C++ ROS node `spot_micro_motion_cmd`
(`spot_micro_motion_cmd/src/spot_micro_motion_cmd.cpp`) is the final stage of
its control pipeline: on every control tick it takes the twelve leg-joint
angles produced by the gait/kinematics code and converts them into commands for
the servo driver board (a PCA9685, driven downstream by the `i2cpwm_board`
node).

This port reproduces the part of that pipeline that is pure translation math —
no ROS, no I²C, no hardware:

1. **`joint_angle_to_proportional`** (from `publishServoProportionalCommand()`):
   each servo has a calibration — the joint angle at its mechanical centre
   (`center_angle_deg`) and a global single-direction travel limit
   (`servo_max_angle_deg = 82.5°`). A commanded angle becomes a *proportional*
   command in `[-1, 1]`: `(cmd_angle − center_angle) / servo_max_angle`, clipped
   to the endpoints.

2. **`proportional_to_pwm_counts`** (from the `i2cpwm_board` "proportional"
   path): the board stores each servo's centre pulse count and range, then maps
   `[-1, 1]` to a raw 12-bit pulse count:
   `center + value · (range / 2) · direction`, clamped to `[0, 4096]`.
   `direction` (`±1`) flips servos whose positive rotation is opposite the
   joint's convention.

3. **`command_all_servos`** runs the whole pipeline for the twelve-servo
   dictionary — one control tick's worth of work — and **`zero_absolute_command`**
   (`publishZeroServoAbsoluteCommand()`) produces the "0 counts everywhere"
   message that limps the servos so they can be back-driven by hand.

The calibration table in `config.py` is copied verbatim from
`spot_micro_motion_cmd.yaml`.

## Translation approach

- **Scope.** Started from the C++ method that actually moves the servos
  (`publishServoProportionalCommand`), traced its inputs back to
  `readInConfigParameters()` and the YAML and its outputs forward into what
  `i2cpwm_board` does with the proportional value. The unit chosen for porting
  is that input → output contract, so it is testable without a robot. ROS
  publishers, the config service call, and `ROS_WARN` logging are out of scope.

- **Types.** The stringly-typed C++ config
  `std::map<std::string, std::map<std::string, float>>` becomes a frozen
  `@dataclass` (`ServoCalibration`), so field names are checked by
  `mypy --strict` and invalid calibration data (`direction` not `±1`, negative
  range, port out of `1..16`) is rejected at construction in `__post_init__`
  rather than producing a silently wrong pulse.

- **Fidelity.** Function names and arithmetic are kept close to the original so
  the port can be diffed against it; each ported function's docstring quotes the
  C++ it came from. The `* M_PI / 180.0` conversions scattered through the C++
  become `math.radians` / `math.degrees`.

- **One deliberate behaviour change.** The C++ handles an out-of-range command
  by logging a warning and clamping to `±1.0`. The port does the same by
  default (`warnings.warn`) but also offers `strict=True`, which raises
  `ProportionalClipError` instead — useful for tests and for callers that would
  rather fail loudly.

- **Tests.** Written around properties that must survive translation: centre
  angle → `0.0` → centre count; linearity and saturation of the proportional
  map; PWM counts never leaving `[0, 4096]`; `direction` reversing the offset;
  the twelve-servo pipeline agreeing end to end.

- **Checks.** `mypy --strict` and `pytest` are both wired into `make check`.

## Possible next steps

- Port `setServoCommandMessageData()`'s mapping from a `LegsJointAngles`
  structure so the input is typed rather than a bare `dict[str, float]`.
- Property-based tests (Hypothesis) for the linearity / monotonicity
  invariants.
