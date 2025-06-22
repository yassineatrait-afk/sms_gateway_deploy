import serial

def send_at_command(port_path, command, baudrate=9600, timeout=1):
    try:
        with serial.Serial(port_path, baudrate, timeout=timeout) as ser:
            ser.write((command + '\r').encode())
            response = ser.readlines()
            return [line.decode(errors='ignore').strip() for line in response]
    except Exception as e:
        return [f"Error: {str(e)}"]
