from brian import *
import time
import sys

def go(distance, accel_dist, decel_dist, max_speed, start_speed, end_speed, run_motor):
    while not run_motor.is_ready():
        print("Motor not ready, waiting...")
        time.sleep(0.1)

    start_dist = run_motor.current_angle()
    print("Starting distance:", start_dist)

    while run_motor.current_angle() - start_dist < distance:
        now_dist = run_motor.current_angle() - start_dist

        # Constant acceleration over time
        if accel_dist > 0:
            f1 = (
                start_speed**2
                + (max_speed**2 - start_speed**2)
                * now_dist / accel_dist
            ) ** 0.5
        else:
            f1 = max_speed

        # Maximum speed
        f2 = max_speed

        # Constant deceleration over time
        if decel_dist > 0:
            remaining_dist = max(0, distance - now_dist)

            f3 = (
                end_speed**2
                + (max_speed**2 - end_speed**2)
                * remaining_dist / decel_dist
            ) ** 0.5
        else:
            f3 = max_speed

        speed = min(f1, f2, f3)

        run_motor.run_at_speed(int(speed))

    run_motor.brake()

go(1200, 300, 300, 600, 200, 200, motors.Motor(motors.MotorPort.D))
time.sleep(1)

