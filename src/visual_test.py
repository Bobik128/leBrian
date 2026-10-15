async def main():
    await crane.moveTo(0.074693, -0.637655, -63.276124, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:8709264163944eb49b827443
    await crane.moveTo(0.272393, -0.638705, -52.116376, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:252ee0b1280f44512fb76fa6
    await crane.moveEndTo(56.65975, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:59ee0f2d2e414b60fd8ace48
    await crane.moveExtendonTo(0.274094, speed=default_extension_speed, acceleration=default_extension_acceleration)  # @crane:a115023da934db11af3c20d7
    await crane.moveEndTo(113.15121, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:3b12e04e6406f6d7a9c539f3
    await asyncio.sleep(0.5)  # @crane:6ea567df4fc92256704bbf26
    await crane.moveEndTo(290.803312, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:cc36d227b2cdd157bcd95908
    await crane.moveYawTo(-76.070651, speed=default_yaw_speed, acceleration=default_yaw_acceleration)  # @crane:7119bc09beb7b637b9a0e57b
    await crane.moveExtendonTo(0.386159, speed=default_extension_speed, acceleration=default_extension_acceleration)  # @crane:1438eba52ffac1b037ff4107
    await crane.moveYawTo(-66.794602, speed=default_yaw_speed, acceleration=default_yaw_acceleration)  # @crane:87a763f4fafdea0c3b9bd3c0
    await crane.moveEndTo(444.206774, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:18c34ac72224595199d3c4e5
    await crane.moveExtendonTo(0.325013, speed=default_extension_speed, acceleration=default_extension_acceleration)  # @crane:a554894b4ef67ff2940e8692
