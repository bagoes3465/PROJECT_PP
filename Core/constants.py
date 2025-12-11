"""Application Constants"""

# File paths
LOG_FILE = r"Data Folder\log_deteksi.csv"
CONFIG_FILE = "app_config.json"
REJECTED_IMAGES_FOLDER = r"Data Folder\rejected_images"

# Detection settings
DETECTION_ZONE_X = 320
DETECTION_ZONE_TOLERANCE = 50
DECISION_COOLDOWN = 2.0
TARGET_FPS = 30

# Emojis for UI
EMOJI = {
    'egg': '🥚', 'settings': '⚙️', 'chart': '📊', 'check': '✅', 
    'cross': '❌', 'camera': '📹', 'brain': '🧠', 'lightning': '⚡',
    'clock': '⏱️', 'bell': '🔔', 'save': '💾', 'folder': '📂',
    'refresh': '🔄', 'upload': '📤', 'play': '▶️', 'stop': '🛑',
    'search': '🔍', 'down': '⬇️', 'usb': '🔌', 'target': '🎯'
}