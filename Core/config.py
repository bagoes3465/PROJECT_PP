import json
import os
import datetime

CONFIG_FILE = "app_config.json"
DETECTION_ZONE_X = 320
DETECTION_ZONE_TOLERANCE = 50
DECISION_COOLDOWN = 2.0


class Config:
    """Configuration manager"""
    def __init__(self):
        self.ip_camera = "192.168.1.6"
        self.min_conf = 0.3
        self.aktifkan_log = True
        self.device = "cpu"
        self.alert_enabled = True
        self.alert_sound_enabled = True
        self.serial_port = ""
        self.serial_baudrate = 9600
        self.detection_zone_x = DETECTION_ZONE_X
        self.detection_zone_tolerance = DETECTION_ZONE_TOLERANCE
        self.decision_cooldown = DECISION_COOLDOWN
        # Camera enhancement settings
        self.camera_enhancement = {}
    
    def load(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    for key in self.__dict__:
                        if key in data:
                            setattr(self, key, data[key])
                print(f"✅ Configuration loaded")
        except Exception as e:
            print(f"Could not load configuration: {e}")
    
    def save(self):
        try:
            data = self.__dict__.copy()
            data["last_saved"] = datetime.datetime.now().isoformat()
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"✅ Configuration saved")
            return True
        except Exception as e:
            print(f"Could not save configuration: {e}")
            return False