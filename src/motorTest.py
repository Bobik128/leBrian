import brian.motors as motors
import time

print("Using A as EV3 large motor")
large = motors.Motor(motors.MotorPort.A)

while True:
    print("CW[A]...")
    large.run_at_speed(200)

    print("Wait...")
    time.sleep(1)

    print("CCW[A]...")
    large.hold()

    print("Wait...")
    time.sleep(1)