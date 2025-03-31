"""Constants for the Tesy integration."""

from homeassistant.const import CONF_IP_ADDRESS

DOMAIN = "tesy"
HTTP_TIMEOUT = 15
UPDATE_INTERVAL = 30

IP_ADDRESS = CONF_IP_ADDRESS
HEATER_POWER = "heater_power"

ATTR_API = "api"

USE_OLD_API = "use_old_api"

# Current software version
ATTR_SOFTWARE = "wsw"

# Mac address of the device
ATTR_MAC = "MAC"

"""Type of the heater
2000 - ModEco With display
2002 - BelliSlimo, only support showers 0-4(maximum depends on size and position)
2003 - BiLight Smart
2004 - Modeco with bar graph and only two buttons
2005 - BelliSlimo Lite, only support showers 0-4(maximum depends on size and position)
"""
ATTR_DEVICE_ID = "id"

# If currently the heater is heating at che moment
ATTR_IS_HEATING = "ht"

# Current temperature measured. Current showers on BelliSlimo.
ATTR_CURRENT_TEMP = "tmpC"

# Target temperature in manual mode, target showers on BelliSlimo. Integer value in both cases.
ATTR_TARGET_TEMP = "tmpT"

# READ-ONLY Target temperature that the controller is using depending on mode. If not on manual it will differ from tmpT.
ATTR_CURRENT_TARGET_TEMP = "tmpR"

"""
Current Operating mode, depending on the device. P1 and P2 heat up in advance so you have the target at the specified time. P3 is like normal thermostat.
0     	manual
1		P1
2		P2
3		P3
4		ECO
5		ECO Confort
6		ECO Night
"""

TESY_MODE_P1 = "P1"
TESY_MODE_P2 = "P2"
TESY_MODE_P3 = "P3"
TESY_MODE_EC2 = "EC2"
TESY_MODE_EC3 = "EC3"

ATTR_MODE = "mode"

# Standby flag, 0 - Off(Antifreeze), 1 - On. If device is off and plugged in will prevent the water from freezing event if off.
ATTR_POWER = "pwr"

# Boost flag 1 - Active, 0 - Inactive. If set Heater will heat once to max, hold there for some time and clear the flag.
ATTR_BOOST = "bst"

# Long time counter, counting seconds the heater was operational. On double tank devices there are  two counters separated by ";" for both heaters.
# There is also pwc_u, it can be reset from UI and holds the last reset timestamp
ATTR_LONG_COUNTER = "pwc_t"

# RSSI
ATTR_RSSI = "wdBm"

ATTR_MAX_SHOWERS = "tmpMX"

ATTR_PARAMETERS = "parNF"

# Additional attributes from the new JSON response
ATTR_TIMEZONE = "tz"
ATTR_PROFILE = "prfl"
ATTR_EXTRA = "extr"
ATTR_DATE = "date"
ATTR_WATER_TIMESTAMP = "wtstp"
ATTR_UPTIME = "wup"
ATTR_HARDWARE_VERSION = "hsw"
ATTR_RESET = "reset"
ATTR_ERROR = "err"
ATTR_CHILD_LOCK = "lck"
ATTR_VACATION = "vac"
ATTR_POSITION = "psn"
ATTR_COUNTDOWN = "cdt"  # Time in minutes until target temperature is reached
ATTR_PIC_TIME = "PICTime"
ATTR_PROGRAM_VACATION = "prgVac"
ATTR_WIFI_IP = "wIP"
ATTR_WIFI_SSID = "wSSID"
ATTR_POWER_CALC = "pwcalc"
ATTR_POWER_COUNTER_USER = "pwc_u"

# ESP32 Discovery and Diagnostic Constants
ATTR_ESP32_ENDPOINTS = "esp32_endpoints"
ATTR_ESP32_SYSTEM_INFO = "esp32_system_info"
ATTR_ESP32_WIFI_INFO = "esp32_wifi_info"
ATTR_ESP32_FILESYSTEM = "esp32_filesystem"
ATTR_ESP32_MEMORY = "esp32_memory"
ATTR_ESP32_CHIP_INFO = "esp32_chip_info"

# Program attributes for each day of the week
ATTR_PROGRAM_P1_MONDAY = "prgP1MO"
ATTR_PROGRAM_P1_TUESDAY = "prgP1TU"
ATTR_PROGRAM_P1_WEDNESDAY = "prgP1WE"
ATTR_PROGRAM_P1_THURSDAY = "prgP1TH"
ATTR_PROGRAM_P1_FRIDAY = "prgP1FR"
ATTR_PROGRAM_P1_SATURDAY = "prgP1SA"
ATTR_PROGRAM_P1_SUNDAY = "prgP1SU"

ATTR_PROGRAM_P2_MONDAY = "prgP2MO"
ATTR_PROGRAM_P2_TUESDAY = "prgP2TU"
ATTR_PROGRAM_P2_WEDNESDAY = "prgP2WE"
ATTR_PROGRAM_P2_THURSDAY = "prgP2TH"
ATTR_PROGRAM_P2_FRIDAY = "prgP2FR"
ATTR_PROGRAM_P2_SATURDAY = "prgP2SA"
ATTR_PROGRAM_P2_SUNDAY = "prgP2SU"

ATTR_PROGRAM_P3_MONDAY = "prgP3MO"
ATTR_PROGRAM_P3_TUESDAY = "prgP3TU"
ATTR_PROGRAM_P3_WEDNESDAY = "prgP3WE"
ATTR_PROGRAM_P3_THURSDAY = "prgP3TH"
ATTR_PROGRAM_P3_FRIDAY = "prgP3FR"
ATTR_PROGRAM_P3_SATURDAY = "prgP3SA"
ATTR_PROGRAM_P3_SUNDAY = "prgP3SU"

"""
Some devices have additional parameters:
"extr" - base64 and url encoded JSON, typically containing custom name if renamed from UI in the Cloud
"lck" - child lock. 1 - Locked, 0 - Unlocked
"cdt" - countdown timer in minutes until target temperature is reached
"tmpMX" - maximum showers could be set on the device, depends on the letter of the heater, and horizontal/vertical position
"psn" - position, 0 - vertical, 1 - horizontal
"wup" - uptime in seconds since last bootup
"parNF" - some additional parameters like volume and power of heaters on doubletank devices
"tz" - timezone string (e.g., "GMT0BST,M3.5.0/1,M10.5.0")
"prfl" - profile/user email
"date" - current date/time on device
"wtstp" - water timestamp
"hsw" - hardware version
"reset" - reset flag
"err" - error code (00 = no error)
"vac" - vacation mode flag
"PICTime" - PIC microcontroller time
"prgVac" - vacation program settings
"wIP" - WiFi IP address
"wSSID" - WiFi SSID name
"wdBm" - WiFi signal strength in dBm
"pwcalc" - power calculation data
"pwc_u" - user resettable power counter with timestamp data
"prgP1MO" to "prgP1SU" - Program P1 schedule for Monday to Sunday
"prgP2MO" to "prgP2SU" - Program P2 schedule for Monday to Sunday  
"prgP3MO" to "prgP3SU" - Program P3 schedule for Monday to Sunday
"""
TESY_DEVICE_TYPES = {
    "2000": {
        "name": "ModEco",
        "min_setpoint": 15,
        "max_setpoint": 75,
    },
    "2002": {
        "name": "BelliSlimo",
        "min_setpoint": 0,
        "max_setpoint": 4,
        "use_showers": True,
    },
    "2003": {
        "name": "BiLight Smart",
        "min_setpoint": 15,
        "max_setpoint": 75,
    },
    "2004": {
        "name": "ModEco 2",
        "min_setpoint": 15,
        "max_setpoint": 75,
    },
    "2005": {
        "name": "BelliSlimo Lite",
        "min_setpoint": 0,
        "max_setpoint": 4,
        "use_showers": True,
    },
}
