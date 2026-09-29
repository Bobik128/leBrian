import brian.sensors as sensors
import brian.sensors.sensor_port_probe as port_probe
import time

print("probe testing on port S1")

while True:
    probe=port_probe.probe_sensor_with_autodetect_hint(sensors.SensorPort.S1, port_probe.AutoDetect.PROTOCOL_UART_EV3)
    print("is connected ", probe.is_connected)
    print(probe.auto_detect)
    print("sensor type name ", probe.info.sensor_type_name)

    time.sleep(1)