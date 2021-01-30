import sys

import serial.tools.list_ports

def get() -> str:
    known_ports = sorted(serial.tools.list_ports.comports())
    port = None
    if len(known_ports) == 0:
        print("No available ports detected.")
        sys.exit(1)
    elif len(known_ports) == 1:
        port = known_ports[0].device
    else:
        for i, port in enumerate(known_ports):
            print(f"  {i+1}: {port.device}")
        pi = input("Select a port number: ") 
        port = known_ports[int(pi)-1].device
    return port