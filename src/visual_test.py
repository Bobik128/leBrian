async def main():
    await crane.moveTo(0.074693, -0.637655, -63.276124, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:231c2f3e41d3f1cfeace0e90
    await crane.moveTo(0.272393, -0.638705, -52.116376, yaw_speed=default_yaw_speed, extendon_speed=default_extension_speed, end_speed=default_end_motor_speed, yaw_acceleration=default_yaw_acceleration, extendon_acceleration=default_extension_acceleration, end_acceleration=default_end_acceleration)  # @crane:8acdada54802017cd340f51b
    await crane.moveEndTo(56.65975, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:a0c62a1cd2a14d828e09e029
    await crane.moveExtendonTo(0.274094, speed=default_extension_speed, acceleration=default_extension_acceleration)  # @crane:9cac96aac5a92fa62d414187
    await crane.moveEndTo(113.15121, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:00bb002ef154ae48b200f769
    await asyncio.sleep(0.5)  # @crane:95bc751b535bc31d5b93a030
    await crane.moveEndTo(290.803312, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:eae8ce0f19280b23f5dec506
    await crane.moveYawTo(-76.070651, speed=default_yaw_speed, acceleration=default_yaw_acceleration)  # @crane:b8ef9af68aefb52b7c0ee4df
    await crane.moveExtendonTo(0.386159, speed=default_extension_speed, acceleration=default_extension_acceleration)  # @crane:45a64f9d87223f7e05ab23cc
    await crane.moveYawTo(-66.794602, speed=default_yaw_speed, acceleration=default_yaw_acceleration)  # @crane:b0c2fb9a66cc9f696d5604a9
    await crane.moveEndTo(444.206774, speed=default_end_motor_speed, acceleration=default_end_acceleration)  # @crane:da3c3cb86299fd748d99e2ec
    await crane.moveExtendonTo(0.325013, speed=default_extension_speed, acceleration=default_extension_acceleration)  # @crane:97376d074b29b2d3120a2108
