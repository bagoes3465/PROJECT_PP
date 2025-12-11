import threading
import time

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("⚠️ PySerial tidak terinstall. Install dengan: pip install pyserial")


class SerialManager:
    """Manage serial communication dengan mikrokontroler"""
    def __init__(self):
        self.serial_port = None
        self.connected = False
        self.lock = threading.Lock()
        
    def list_ports(self):
        """List available serial ports"""
        if not SERIAL_AVAILABLE:
            return []
        ports = serial.tools.list_ports.comports()
        return [(port.device, port.description) for port in ports]
    
    def connect(self, port, baudrate=9600):
        """Connect ke serial port"""
        try:
            with self.lock:
                if self.connected:
                    self.disconnect()
                
                self.serial_port = serial.Serial(port, baudrate, timeout=1)
                time.sleep(2)
                self.connected = True
                print(f"✅ Connected to {port} at {baudrate} baud")
                return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect dari serial port"""
        try:
            with self.lock:
                if self.serial_port and self.connected:
                    self.serial_port.close()
                    self.connected = False
                    print("🔌 Serial disconnected")
                    return True
        except Exception as e:
            print(f"Error disconnecting: {e}")
        return False
    
    def send_decision(self, decision):
        """Kirim keputusan ke mikrokontroler"""
        if not self.connected or not self.serial_port:
            return False
        
        try:
            with self.lock:
                command = 'A' if decision == "ACCEPT" else 'R'
                self.serial_port.write(command.encode())
                self.serial_port.flush()
                print(f"📤 Sent to Arduino: {command} ({decision})")
                return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False