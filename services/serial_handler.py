import serial

def send_at_command(port_path, command, baudrate=9600, timeout=1):
    try:
        with serial.Serial(port_path, baudrate, timeout=timeout) as ser:
            ser.write((command + '\r').encode())
            response = ser.readlines()
            return [line.decode(errors='ignore').strip() for line in response]
    except Exception as e:
        return [f"Error: {str(e)}"]

def send_ussd(port_path, ussd_code, baudrate=9600, timeout=5):
    """
    Send a USSD request wrapped in AT+CUSD.
    """
    cmd = f'AT+CUSD=1,"{ussd_code}",15'
    return send_at_command(port_path, cmd, baudrate=baudrate, timeout=timeout)

