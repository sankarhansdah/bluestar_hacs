"""Constants for Bluestar Smart AC integration."""

DOMAIN = "bluestar_ac"
MANUFACTURER = "Bluestar"

# Configuration keys
CONF_MQTT_GATEWAY_URL = "mqtt_gateway_url"
CONF_PHONE = "phone"
CONF_PASSWORD = "password"
CONF_BASE_URL = "base_url"

# Default values
DEFAULT_BASE_URL = "https://api.bluestarindia.com/prod"
DEFAULT_SCAN_INTERVAL = 5  # seconds

# Bluestar API endpoints
BLUESTAR_BASE_URL = "https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod"
LOGIN_ENDPOINT = "/auth/login"
DEVICES_ENDPOINT = "/things"
CONTROL_ENDPOINT = "/things/{device_id}/control"
PREFERENCES_ENDPOINT = "/things/{device_id}/preferences"
STATE_ENDPOINT = "/things/{device_id}/state"

# Headers (exact match from working server.js)
HEADERS = {
    "X-APP-VER": "v4.11.4-133",
    "X-OS-NAME": "Android",
    "X-OS-VER": "v13-33",
    "User-Agent": "com.bluestarindia.bluesmart",
    "Content-Type": "application/json",
}

# HVAC Mode mappings (HA -> Bluestar)
HVAC_MODE_TO_BLUESTAR = {
    "off": {"pow": 0},
    "fan_only": {"pow": 1, "mode": 0},
    "cool": {"pow": 1, "mode": 2},
    "dry": {"pow": 1, "mode": 3},
    "auto": {"pow": 1, "mode": 4},
}

# Bluestar -> HA HVAC Mode mappings
BLUESTAR_TO_HVAC_MODE = {
    0: "fan_only",  # pow=1, mode=0
    2: "cool",      # pow=1, mode=2
    3: "dry",       # pow=1, mode=3
    4: "auto",      # pow=1, mode=4
}

# Fan speed mappings (HA -> Bluestar)
FAN_MODE_TO_BLUESTAR = {
    "low": 2,
    "medium": 3,
    "high": 4,
    "auto": 7,
    "turbo": 6,  # Keep for future use
}

# Bluestar -> HA Fan Mode mappings
BLUESTAR_TO_FAN_MODE = {
    2: "low",
    3: "medium",
    4: "high",
    6: "high",  # Map turbo to high for now
    7: "auto",
}

# Swing mappings
SWING_OPTIONS = [
    {"label": "Off", "value": 0},
    {"label": "15°", "value": 1},
    {"label": "30°", "value": 2},
    {"label": "45°", "value": 3},
    {"label": "60°", "value": 4},
    {"label": "Auto", "value": -1},
]

SWING_LABEL_TO_VALUE = {option["label"]: option["value"] for option in SWING_OPTIONS}
SWING_VALUE_TO_LABEL = {option["value"]: option["label"] for option in SWING_OPTIONS}

# Temperature range
MIN_TEMP = 16.0
MAX_TEMP = 30.0
TEMP_STEP = 0.5

# MQTT constants (from exact_mqtt_client.js)
MQTT_SRC_KEY = "src"
MQTT_SRC_VALUE = "anmq"
MQTT_FORCE_SYNC_KEY = "fpsh"
MQTT_CONTROL_TOPIC = "things/{device_id}/control"
MQTT_SHADOW_UPDATE_TOPIC = "$aws/things/{device_id}/shadow/update"

# Device state keys
STATE_POWER = "pow"
STATE_MODE = "mode"
STATE_TEMP = "stemp"
STATE_CURRENT_TEMP = "ctemp"
STATE_FAN_SPEED = "fspd"
STATE_VERTICAL_SWING = "vswing"
STATE_HORIZONTAL_SWING = "hswing"
STATE_DISPLAY = "display"
STATE_RSSI = "rssi"
STATE_ERROR = "err"
STATE_SOURCE = "src"
STATE_CONNECTED = "connected"

# Error messages
ERROR_LOGIN_FAILED = "Login failed"
ERROR_DEVICE_NOT_FOUND = "Device not found"
ERROR_CONTROL_FAILED = "Control command failed"
ERROR_MQTT_NOT_CONNECTED = "MQTT client not connected"
ERROR_SESSION_EXPIRED = "Session expired"
