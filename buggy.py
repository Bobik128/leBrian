from brian import *
import time
import math
import asyncio

lMotor: motors.Motor
rMotor: motors.Motor

def init(leftMotor: motors.MotorPort, rightMotor: motors.MotorPort):
    global lMotor, rMotor
    lMotor = motors.Motor(leftMotor)
    rMotor = motors.Motor(rightMotor)

async def moveTank(lSpeed: float, rSpeed: float, dist: float, stopBool: bool = True):
    global lMotor, rMotor
    startLAngle = lMotor.current_angle()
    startRAngle = rMotor.current_angle()

    lMotor.hold()
    rMotor.hold()

    lMotor.run_at_speed(math.floor(lSpeed))
    rMotor.run_at_speed(math.floor(rSpeed))

    # while getRelativeAbsAngle(startLAngle, startRAngle) < abs(dist):
    while getRelativeAbsAngle(startLAngle, startRAngle) < abs(dist):
        await asyncio.sleep(0.01) 

    if stopBool: stop()

def getRelativeAbsAngle(startLAngle: float, startRAngle: float):
    return (abs(lMotor.current_angle() - startLAngle) + abs(rMotor.current_angle() - startRAngle)) / 2

def getAbsoluteAngle():
    return (lMotor.current_angle + rMotor.current_angle) / 2

async def steering(speed: float, dist: float, steering: float = 0):
    startLAngle = lMotor.current_angle()
    startRAngle = rMotor.current_angle()

    dir = getDir(speed, dist)
    buggySpeedSetterUtil(dir, steering, abs(speed))

    while getRelativeAbsAngle(startLAngle, startRAngle) < abs(dist):
        await asyncio.sleep(0.01)

    stop()

def speedControler(speed: float, input: float, direction: bool):
    limitSpeed: float = speed * (3/2)
    if direction:
        if abs(speed + input) >= limitSpeed:
            regulatedSpeed = limitSpeed
        else:
            regulatedSpeed = abs(speed + input)
    else:
        if abs(speed - input) >= limitSpeed:
            regulatedSpeed = limitSpeed
        else:
            regulatedSpeed = abs(speed - input)

    return regulatedSpeed

def buggySpeedSetterUtil(dir: bool, input: float, speed: float):
    if dir:
        s1: int = math.floor(speedControler(speed, input, True))
        s2: int = math.floor(speedControler(speed, input, False))
        if abs(input) > speed:
            if input < 0:
                rMotor.run_at_speed(-s1)
                lMotor.run_at_speed(s2)
            else:
                rMotor.run_at_speed(s1)
                lMotor.run_at_speed(-s2)
        else:
            rMotor.run_at_speed(s1)
            lMotor.run_at_speed(s2)
    else:
        s1: int = math.floor(speedControler(speed, -input, True))
        s2: int = math.floor(speedControler(speed, -input, False))
        if abs(input) > speed:
            if input >= 0:
                rMotor.run_at_speed(s1)
                lMotor.run_at_speed(-s2)
            else:
                rMotor.run_at_speed(-s1)
                lMotor.run_at_speed(s2)
        else:
            rMotor.run_at_speed(-s1)
            lMotor.run_at_speed(-s2)

def getDir(speed: float, dist: float):
    if speed < 0:
        dist *= -1
    
    return dist > 0

def resetAngle():
    rMotor.reset_angle()
    lMotor.reset_angle()

def stop():
    # lMotor.hold()
    # rMotor.hold()
    lMotor.brake()
    rMotor.brake()

def brake():
    lMotor.brake()
    rMotor.brake()