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

async def moveTank(lSpeed: int, rSpeed: int, dist: float):
    startLAngle = lMotor.current_angle()
    startRAngle = rMotor.current_angle()

    lMotor.run_at_speed(lSpeed)
    rMotor.run_at_speed(rSpeed)

    while getRelativeAbsAngle(startLAngle, startRAngle) < abs(dist):
        
        await asyncio.sleep(0.01) 

    lMotor.hold()
    rMotor.hold()
    print("Motors stopped")

def getRelativeAbsAngle(startLAngle: float, startRAngle: float):
    return (abs(lMotor.current_angle() - startLAngle) + abs(rMotor.current_angle() - startRAngle)) / 2

def getAbsoluteAngle():
    return (lMotor.current_angle + rMotor.current_angle) / 2

async def steering(speed: float, dist: float, steering: float):
    startLAngle = lMotor.current_angle()
    startRAngle = rMotor.current_angle()

    dir = getDir(speed, dist)
    buggySpeedSetterUtil(dir, steering, speed)

    while getRelativeAbsAngle(startLAngle, startRAngle) < abs(dist):
        await asyncio.sleep(0.01)

    lMotor.hold()
    rMotor.hold()

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

def stop():
    lMotor.hold()
    rMotor.hold()