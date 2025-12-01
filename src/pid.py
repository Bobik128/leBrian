from brian import *
import buggy
import brick
import asyncio
import math
import time

Kp: float
Ki: float
Kd: float

rKp: float
rKi: float
rKd: float

lKp: float
lKi: float
lKd: float

lightTarget: int = 60

def isStuck(lastCheckTime, lastError, error):
    currentTime = time.time()

    if currentTime - lastCheckTime < 1:
        return False, lastCheckTime, lastError
    
    if abs(error) >= 20:
        if lastError > 0 and lastError - error < 5:
            return True, currentTime, error
        elif lastError < 0 and lastError - error > -5:
            return True, currentTime, error
    return False, currentTime, error

async def waitForPress():
    listener: uicontrol.UiEventsListener = uicontrol.UiEventsListener()
    while True:
        knob: uicontrol.UiEventsListener.KnobEvent = listener.knob_event_since_last()
        if knob.just_pressed:
            break

async def initLineFollower(p, i, d):
    global lightTarget, lKp, lKi, lKd
    lKp = p
    lKi = i
    lKd = d
    brick.color
    brick.color.reflected_value()
    print("Init color")
    await waitForPress()
    lightTarget = brick.color.reflected_value()

def init(kp: float, ki: float, kd: float, rkp: float, rki: float, rkd: float):
    global Kp, Ki, Kd, rKp, rKi, rKd
    Kp = kp
    Ki = ki
    Kd = kd

    rKp = rkp
    rKi = rki
    rKd = rkd

# ========== GO FIXED DISTANCE ==========
async def goForDegrees(
    targetAngle: float,
    dist: float,
    speed: float,
    stopAtEnd: bool = True,

    accelDist: float = 5.0,
    startAccelFactor: float = 0.40,
    decelDist: float = 20.0,
    endDecelFactor: float = 0.45,
):
    dir = buggy.getDir(speed, dist)
    baseSpeed = float(abs(speed))

    startLAngle = buggy.lMotor.current_angle()
    startRAngle = buggy.rMotor.current_angle()
    absDist = abs(dist)

    integral = 0.0
    lastError = 0.0

    lastCheckTime = time.time()
    lastStuckError = 0.0

    def clamp(x, lo, hi): return hi if x > hi else lo if x < lo else x
    def lerp(a, b, t): return a + (b - a) * t

    def accel_factor(traveled: float) -> float:
        if accelDist <= 0: return 1.0
        t = clamp(traveled / float(accelDist), 0.0, 1.0)
        return lerp(startAccelFactor, 1.0, t)

    def decel_factor(remaining: float) -> float:
        if decelDist <= 0: return 1.0
        # start decel when remaining <= decelDist
        t = clamp((decelDist - remaining) / float(decelDist), 0.0, 1.0)
        return lerp(1.0, endDecelFactor, t)

    while buggy.getRelativeAbsAngle(startLAngle, startRAngle) < absDist:
        traveled = buggy.getRelativeAbsAngle(startLAngle, startRAngle)
        remaining = max(0.0, absDist - traveled)

        a = accel_factor(traveled)
        d = decel_factor(remaining)
        m = clamp(a * d, min(startAccelFactor, endDecelFactor), 1.0)
        curr_speed = baseSpeed * m

        # heading PID
        error = targetAngle + brick.gyro.angle()
        output = Kp * error + Ki * integral + Kd * (error - lastError)

        buggy.buggySpeedSetterUtil(dir, output, curr_speed - abs(output))

        # stuck handling
        stuck, lastCheckTime, lastStuckError = isStuck(lastCheckTime, lastStuckError, error)
        if stuck:
            buggy.brake()
            s_val = -int(curr_speed) if dir else int(curr_speed)
            await buggy.moveTank(s_val, s_val, 120)
            startLAngle = buggy.lMotor.current_angle()
            startRAngle = buggy.rMotor.current_angle()  # re-baseline ramps

        integral = clamp(integral + error, -100.0, 100.0)
        lastError = error
        await asyncio.sleep(0.05)

    if stopAtEnd:
        buggy.stop()

# ========== GO UNTIL LINE ==========
async def goTilLine(
    targetAngle: float,
    speed: float,
    stopAtEnd: bool = True,
    timeout: float = 5.0,

    middle: int = 60,

    maxDist: float = 2000.0,

    accelDist: float = 60.0,
    startAccelFactor: float = 0.3,
    decelDist: float = 140.0,
    endDecelFactor: float = 0.35,

    postDecelDist: float = 0.0,
):
    dir = buggy.getDir(speed, 1)
    baseSpeed = float(abs(speed))

    startLAngle = buggy.lMotor.current_angle()
    startRAngle = buggy.rMotor.current_angle()
    absDist = float(abs(maxDist))

    integral = 0.0
    lastError = 0.0
    startTime = time.time()
    last_m = 0.0  # store multiplier at trigger

    def clamp(x, lo, hi): return hi if x > hi else lo if x < lo else x
    def lerp(a, b, t): return a + (b - a) * t

    def accel_factor(traveled: float) -> float:
        if accelDist <= 0: return 1.0
        t = clamp(traveled / float(accelDist), 0.0, 1.0)
        return lerp(startAccelFactor, 1.0, t)

    def pre_decel_factor(traveled: float) -> float:
        if decelDist <= 0: return 1.0
        decel_start = max(0.0, absDist - float(decelDist))
        if traveled < decel_start:
            return 1.0
        t = clamp((traveled - decel_start) / max(1e-9, float(decelDist)), 0.0, 1.0)
        return lerp(1.0, endDecelFactor, t)

    # ---------- pre-trigger ----------
    while brick.color.reflected_value() > middle and (time.time() - startTime) < timeout:
        traveled = buggy.getRelativeAbsAngle(startLAngle, startRAngle)

        a = accel_factor(traveled)
        d = pre_decel_factor(traveled)
        m = clamp(a * d, min(startAccelFactor, endDecelFactor), 1.0)
        last_m = m
        curr_speed = baseSpeed * m

        error = targetAngle + brick.gyro.angle()
        output = Kp * error + Ki * integral + Kd * (error - lastError)
        buggy.buggySpeedSetterUtil(dir, output, curr_speed)

        integral = clamp(integral + error, -100.0, 100.0)
        lastError = error
        await asyncio.sleep(0.03)

    # ---------- post-trigger decel ----------
    if brick.color.reflected_value() <= middle and postDecelDist > 0.0:
        postStartL = buggy.lMotor.current_angle()
        postStartR = buggy.rMotor.current_angle()
        postDist = float(abs(postDecelDist))

        while buggy.getRelativeAbsAngle(postStartL, postStartR) < postDist:
            t = buggy.getRelativeAbsAngle(postStartL, postStartR) / max(1e-9, postDist)
            # ramp multiplier from m_at_trigger -> endDecelFactor
            m = lerp(last_m, endDecelFactor, min(1.0, t))
            curr_speed = baseSpeed * m

            error = targetAngle + brick.gyro.angle()
            output = Kp * error + Ki * integral + Kd * (error - lastError)
            buggy.buggySpeedSetterUtil(dir, output, curr_speed)

            integral = clamp(integral + error, -100.0, 100.0)
            lastError = error
            await asyncio.sleep(0.01)

    if stopAtEnd:
        buggy.stop()

# ========== GO UNTIL BUTTON ==========
async def goTilButton(
    targetAngle: float,
    spd: float,
    button: sensors.EV3.TouchSensorEV3,
    stopDelay: int = 0,
    timeout: float = 7.0,

    maxDist: float = 2000.0,

    accelDist: float = 60.0,
    startAccelFactor: float = 0.3,
    decelDist: float = 140.0,
    endDecelFactor: float = 0.35,

    postDecelDist: float = 0.0,
):
    dir = buggy.getDir(spd, 1)
    baseSpeed = float(abs(spd))

    startLAngle = buggy.lMotor.current_angle()
    startRAngle = buggy.rMotor.current_angle()
    absDist = float(abs(maxDist))

    integral = 0.0
    lastError = 0.0
    startTime = time.time()

    lastCheckTime = time.time()
    lastStuckError = 0.0
    last_m = 0.0

    def clamp(x, lo, hi): return hi if x > hi else lo if x < lo else x
    def lerp(a, b, t): return a + (b - a) * t

    def accel_factor(traveled: float) -> float:
        if accelDist <= 0: return 1.0
        t = clamp(traveled / float(accelDist), 0.0, 1.0)
        return lerp(startAccelFactor, 1.0, t)

    def pre_decel_factor(traveled: float) -> float:
        if decelDist <= 0: return 1.0
        decel_start = max(0.0, absDist - float(decelDist))
        if traveled < decel_start:
            return 1.0
        t = clamp((traveled - decel_start) / max(1e-9, float(decelDist)), 0.0, 1.0)
        return lerp(1.0, endDecelFactor, t)

    # ---------- pre-trigger ----------
    while not button.is_pressed() and (time.time() - startTime) < timeout:
        traveled = buggy.getRelativeAbsAngle(startLAngle, startRAngle)

        a = accel_factor(traveled)
        d = pre_decel_factor(traveled)
        m = clamp(a * d, min(startAccelFactor, endDecelFactor), 1.0)
        last_m = m
        curr_speed = baseSpeed * m

        error = targetAngle + brick.gyro.angle()
        output = Kp * error + Ki * integral + Kd * (error - lastError)
        buggy.buggySpeedSetterUtil(dir, output, curr_speed)

        # stuck detection
        stuck, lastCheckTime, lastStuckError = isStuck(lastCheckTime, lastStuckError, error)
        if stuck:
            buggy.brake()
            s_val = -int(curr_speed) if dir else int(curr_speed)
            await buggy.moveTank(s_val, s_val, 120)
            startLAngle = buggy.lMotor.current_angle()
            startRAngle = buggy.rMotor.current_angle()

        integral = clamp(integral + error, -100.0, 100.0)
        lastError = error
        await asyncio.sleep(0.02)

    # ---------- post-trigger decel ----------
    if button.is_pressed() and postDecelDist > 0.0:
        postStartL = buggy.lMotor.current_angle()
        postStartR = buggy.rMotor.current_angle()
        postDist = float(abs(postDecelDist))

        while buggy.getRelativeAbsAngle(postStartL, postStartR) < postDist:
            t = buggy.getRelativeAbsAngle(postStartL, postStartR) / max(1e-9, postDist)
            m = lerp(last_m, endDecelFactor, min(1.0, t))
            curr_speed = baseSpeed * m

            error = targetAngle + brick.gyro.angle()
            output = Kp * error + Ki * integral + Kd * (error - lastError)
            buggy.buggySpeedSetterUtil(dir, output, curr_speed)

            integral = clamp(integral + error, -100.0, 100.0)
            lastError = error
            await asyncio.sleep(0.01)

    await asyncio.sleep(stopDelay)
    buggy.stop()

async def lineFollowerWithGyro(angle: int, speed: float, dist: int):
    global lightTarget
    speed = abs(speed)

    brick.color
    brick.color.reflected_value()

    startLAngle = buggy.lMotor.current_angle()
    startRAngle = buggy.rMotor.current_angle()
    absDist: float = abs(dist)

    await asyncio.sleep(0.5)

    integral: float = 0
    lastError: float = 0

    while buggy.getRelativeAbsAngle(startLAngle, startRAngle) < absDist:
        error: float = lightTarget - brick.color.reflected_value()
        output: float = lKp * error + lKi * integral + lKd * (error - lastError)

        if brick.gyro.angle() + angle > 5 and output > 0:
            output = 0
            error = 0
        elif brick.gyro.angle() + angle < -5 and output < 0:
            output = 0
            error = 0

        buggy.buggySpeedSetterUtil(True, -output, speed)

        integral += error
        lastError = error

        if integral < -100:
            integral = -100
        elif integral > 100:
            integral = 100


        await asyncio.sleep(0.01)

async def lineFollowerWithGyroTilButton(angle: int, speed: float, button: sensors.EV3.TouchSensorEV3, delay: float):
    global lightTarget
    speed = abs(speed)

    brick.color
    brick.color.reflected_value()

    await asyncio.sleep(0.5)

    integral: float = 0
    lastError: float = 0

    while not button.is_pressed():
        error: float = lightTarget - brick.color.reflected_value()
        output: float = lKp * error + lKi * integral + lKd * (error - lastError)

        if brick.gyro.angle() + angle > 5 and output > 0:
            output = 0
        elif brick.gyro.angle() + angle < -5 and output < 0:
            output = 0

        buggy.buggySpeedSetterUtil(True, -output, speed)

        integral += error
        lastError = error

        if integral < -100:
            integral = -100
        elif integral > 100:
            integral = 100


        await asyncio.sleep(0.01)

async def turnTo(
    targetAngle: int,
    tolerance: int,
    speed: int,
    left_powerup: int = 0,
    right_powerup: int = 0,
    stopAtEnd: bool = True,
    
    accelAngle: float = 10.0,         # degrees of rotation over which to ramp the multiplier
    startAccelFactor: float = 0.3,    # multiplier at start
):
    nowDir: int = brick.gyro.angle()
    if nowDir == targetAngle:
        return

    startAngle = nowDir
    integral: float = 0.0
    lastError: float = 0.0

    lastCheckTime = time.time()
    lastStuckError = 0.0

    speedLimit: float = 600.0

    def clamp(x, lo, hi):
        return hi if x > hi else lo if x < lo else x

    def accel_factor(traveled_deg: float) -> float:
        """Linear ramp multiplier from startAccelFactor -> 1.0 over accelAngle."""
        if accelAngle <= 0:
            return 1.0
        t = clamp(traveled_deg / float(accelAngle), 0.0, 1.0)
        return startAccelFactor + (1.0 - startAccelFactor) * t

    await asyncio.sleep(0.04)
    while abs(targetAngle + nowDir) > tolerance:
        nowDir = brick.gyro.angle()

        # PID
        error: float = targetAngle + nowDir
        output: float = rKp * error + rKi * integral + rKd * (error - lastError)

        # how much already rotated since start (for accel ramp)
        traveled = abs(nowDir - startAngle)
        a = accel_factor(traveled)

        lSpeed: float = -output * (speed + left_powerup) * a
        rSpeed: float =  output * (speed + right_powerup) * a

        lSpeed = clamp(lSpeed, -speedLimit, speedLimit)
        rSpeed = clamp(rSpeed, -speedLimit, speedLimit)

        buggy.lMotor.run_at_speed(math.floor(lSpeed))
        buggy.rMotor.run_at_speed(math.floor(rSpeed))

        stuck, lastCheckTime, lastStuckError = isStuck(lastCheckTime, lastStuckError, error)
        if stuck:
            buggy.brake()
            nudge = int(max(80, abs(speed) * a))
            buggy.lMotor.run_at_speed(-nudge)
            buggy.rMotor.run_at_speed(+nudge)
            await asyncio.sleep(0.12)
            startAngle = brick.gyro.angle()

        ILimit: float = 15.0
        integral += error
        integral = clamp(integral, -ILimit, ILimit)
        lastError = error

        await asyncio.sleep(0.04)

    if stopAtEnd:
        buggy.stop()
