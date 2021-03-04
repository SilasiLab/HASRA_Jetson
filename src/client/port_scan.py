import serial.tools.list_ports

# this just uses some tool to scan for devices connected to com ports and searches their strings for hardcoded substrings

def get_com_ports():
    ard_port = 'COMx'
    rfid_port = 'COMx'

    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if 'USB Serial' in p.description:
            ard_port = p[0]
        if 'UART' in p.description:
            rfid_port = p[0]
    return ard_port, rfid_port
