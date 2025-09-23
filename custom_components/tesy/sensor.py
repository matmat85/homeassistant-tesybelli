"""Tesy sensor component."""

from __future__ import annotations
import base64
import json
from urllib.parse import unquote
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfEnergy, 
    UnitOfTemperature, 
    UnitOfTime,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import TesyEntity
from .const import (
    ATTR_PARAMETERS,
    DOMAIN,
    ATTR_LONG_COUNTER,
    ATTR_CURRENT_TEMP,
    ATTR_RSSI,
    ATTR_UPTIME,
    ATTR_COUNTDOWN,
    ATTR_ERROR,
    ATTR_HARDWARE_VERSION,
    ATTR_WIFI_IP,
    ATTR_WIFI_SSID,
    ATTR_EXTRA,
    ATTR_CHILD_LOCK,
    ATTR_VACATION,
    ATTR_POSITION,
    ATTR_MODE,
    ATTR_TARGET_TEMP,
    ATTR_CURRENT_TARGET_TEMP,
    ATTR_IS_HEATING,
    ATTR_POWER,
    ATTR_BOOST,
    ATTR_DATE,
    ATTR_MAC,
    ATTR_SOFTWARE,
    ATTR_DEVICE_ID,
    ATTR_TIMEZONE,
    ATTR_PROFILE,
    ATTR_MAX_SHOWERS,
    ATTR_RESET,
    ATTR_PROGRAM_VACATION,
)
from .coordinator import TesyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Tesy devices from config entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        TesyTemperatureSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="temperature",
                name="Temperature",
                device_class=SensorDeviceClass.TEMPERATURE,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                icon="mdi:thermometer",
            ),
            0.1,
            None,
        ),
        TesyEnergySensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="energy_consumed",
                name="Energy Consumed",
                device_class=SensorDeviceClass.ENERGY,
                state_class=SensorStateClass.TOTAL_INCREASING,
                native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
                icon="mdi:lightning-bolt",
            ),
            0.01,
            None,
        ),
        TesyRSSISensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="wifi_signal",
                name="WiFi Signal Strength",
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
                icon="mdi:wifi",
            ),
            None,
            None,
        ),
        TesyUptimeSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="uptime",
                name="Uptime",
                device_class=SensorDeviceClass.DURATION,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement=UnitOfTime.SECONDS,
                icon="mdi:clock-outline",
            ),
            None,
            None,
        ),
        TesyCountdownSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="countdown",
                name="Countdown Timer",
                device_class=SensorDeviceClass.DURATION,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement=UnitOfTime.MINUTES,
                icon="mdi:timer-outline",
            ),
            None,
            None,
        ),
        TesyErrorSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="error_code",
                name="Error Code",
                icon="mdi:alert-circle-outline",
            ),
            None,
            None,
        ),
        TesyHardwareVersionSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="hardware_version",
                name="Hardware Version",
                icon="mdi:chip",
            ),
            None,
            None,
        ),
        TesyWiFiIPSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="wifi_ip",
                name="WiFi IP Address",
                icon="mdi:ip-network",
            ),
            None,
            None,
        ),
        TesyWiFiSSIDSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="wifi_ssid",
                name="WiFi SSID",
                icon="mdi:wifi",
            ),
            None,
            None,
        ),
        TesyDeviceNameSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="device_name",
                name="Device Name",
                icon="mdi:tag-outline",
            ),
            None,
            None,
        ),
        TesyPositionSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="position",
                name="Installation Position",
                icon="mdi:rotate-3d-variant",
            ),
            None,
            None,
        ),
        TesyMemoryUsageSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="memory_usage",
                name="Free Memory",
                device_class=SensorDeviceClass.DATA_SIZE,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement="KB",
                icon="mdi:memory",
            ),
            None,
            None,
        ),
        TesyBootReasonSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="boot_reason",
                name="Last Boot Reason",
                icon="mdi:restart",
            ),
            None,
            None,
        ),
        TesyFirmwareBuildSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="firmware_build",
                name="Firmware Build Date",
                icon="mdi:calendar-clock",
            ),
            None,
            None,
        ),
        TesyETASensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="ready_eta",
                name="Ready ETA",
                device_class=SensorDeviceClass.TIMESTAMP,
                icon="mdi:clock-end",
            ),
            None,
            None,
        ),
        TesyModeTextSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="mode_text",
                name="Operation Mode",
                icon="mdi:water-boiler",
            ),
            None,
            None,
        ),
        TesyErrorTextSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="error_text",
                name="Error Description",
                icon="mdi:alert-circle-outline",
            ),
            None,
            None,
        ),
        TesyStatusSnapshotSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="status_snapshot",
                name="Full Status Snapshot",
                icon="mdi:file-code-outline",
            ),
            None,
            None,
        ),
        TesyDiagnosticSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="diagnostic",
                name="API Response",
                icon="mdi:code-json",
            ),
            None,
            None,
        ),
        TesyESP32DiscoverySensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="esp32_discovery",
                name="ESP32 Discovery",
                icon="mdi:chip",
            ),
            None,
            None,
        ),
    ]
    
    async_add_entities(sensors)


class TesySensor(TesyEntity, SensorEntity):
    """Represents a sensor for a Tesy water heater controller."""

    _attr_has_entity_name = True
    _attr_should_poll = True

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: TesyCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
        suggested_precision: float | None,
        options: list | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(hass, coordinator, entry, description)

        self.entity_description = description
        self._attr_name = description.name

        if description.device_class is not None:
            self._attr_device_class = description.device_class

        if description.state_class is not None:
            self._attr_state_class = description.state_class

        if description.native_unit_of_measurement is not None:
            self._attr_native_unit_of_measurement = (
                description.native_unit_of_measurement
            )

        if description.icon is not None:
            self._attr_icon = description.icon

        if suggested_precision is not None:
            self._attr_suggested_display_precision = suggested_precision

        if options is not None:
            self._attr_options = options


class TesyEnergySensor(TesySensor):
    @property
    def native_value(self):
        """Return the state of the sensor."""
        # Prevent crashes if energy counter is missing
        if ATTR_LONG_COUNTER not in self.coordinator.data:
            return None

        if ";" not in self.coordinator.data[ATTR_LONG_COUNTER]:
            # For single tank heaters, we need to have power value configured
            configured_power = self.coordinator.get_config_power()
            energy_kwh = (
                int(self.coordinator.data[ATTR_LONG_COUNTER]) * configured_power
            ) / (3600.0 * 1000)
            return energy_kwh
        else:
            # Prevent crashes if Additional parameters are missing
            if ATTR_PARAMETERS not in self.coordinator.data:
                return None

            power_dict = self.coordinator.data[ATTR_LONG_COUNTER].split(";")
            pNF = self.coordinator.data[ATTR_PARAMETERS]
            watt1 = int(pNF[38 + 0 * 2 : 40 + 0 * 2], 16) * 20
            watt2 = int(pNF[38 + 1 * 2 : 40 + 1 * 2], 16) * 20
            tmp_kwh1 = (int(power_dict[0]) * watt1) / (3600.0 * 1000)
            tmp_kwh2 = (int(power_dict[1]) * watt2) / (3600.0 * 1000)

            return tmp_kwh1 + tmp_kwh2


class TesyTemperatureSensor(TesySensor):
    @property
    def native_value(self):
        """Return the state of the sensor."""
        if ATTR_CURRENT_TEMP not in self.coordinator.data:
            return None
        return float(self.coordinator.data[ATTR_CURRENT_TEMP]) 


class TesyRSSISensor(TesySensor):
    @property
    def native_value(self):
        """Return the WiFi signal strength."""
        if ATTR_RSSI not in self.coordinator.data:
            return None
        return int(self.coordinator.data[ATTR_RSSI]) 


class TesyUptimeSensor(TesySensor):
    @property
    def native_value(self):
        """Return the device uptime in seconds."""
        if ATTR_UPTIME not in self.coordinator.data:
            return None
        return int(self.coordinator.data[ATTR_UPTIME]) 


class TesyCountdownSensor(TesySensor):
    @property
    def native_value(self):
        """Return the countdown timer value in minutes until target temperature is reached."""
        if ATTR_COUNTDOWN not in self.coordinator.data:
            return None
        return int(self.coordinator.data[ATTR_COUNTDOWN]) 

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return additional attributes for the countdown sensor."""
        if ATTR_COUNTDOWN not in self.coordinator.data:
            return None
        
        countdown_minutes = int(self.coordinator.data[ATTR_COUNTDOWN])
        return {
            "countdown_minutes": countdown_minutes,
            "countdown_seconds": countdown_minutes * 60,
            "description": "Time remaining until target temperature is reached"
        }


class TesyErrorSensor(TesySensor):
    @property
    def native_value(self):
        """Return the error code."""
        if ATTR_ERROR not in self.coordinator.data:
            return None
        error_code = self.coordinator.data[ATTR_ERROR]
        return error_code if error_code != "00" else "No Error"


class TesyHardwareVersionSensor(TesySensor):
    @property
    def native_value(self):
        """Return the hardware version."""
        if ATTR_HARDWARE_VERSION not in self.coordinator.data:
            return None
        return self.coordinator.data[ATTR_HARDWARE_VERSION] 


class TesyWiFiIPSensor(TesySensor):
    @property
    def native_value(self):
        """Return the WiFi IP address."""
        if ATTR_WIFI_IP not in self.coordinator.data:
            return None
        return self.coordinator.data[ATTR_WIFI_IP] 


class TesyWiFiSSIDSensor(TesySensor):
    @property
    def native_value(self):
        """Return the WiFi SSID."""
        if ATTR_WIFI_SSID not in self.coordinator.data:
            return None
        return self.coordinator.data[ATTR_WIFI_SSID] 


class TesyDeviceNameSensor(TesySensor):
    @property
    def native_value(self):
        """Return the custom device name or timezone from extra field."""
        if ATTR_EXTRA not in self.coordinator.data:
            return None
        
        try:
            # Decode the base64 and URL encoded extra field
            extra_data = self.coordinator.data[ATTR_EXTRA]
            decoded = unquote(extra_data)
            json_data = base64.b64decode(decoded).decode('utf-8')
            extra_info = json.loads(json_data)
            
            # Return timezone name if available, otherwise return the device type
            return extra_info.get("tzname", "Unknown")
        except (ValueError, json.JSONDecodeError, KeyError, Exception):
            # If decoding fails, try to parse as simple timezone string
            try:
                decoded = unquote(self.coordinator.data[ATTR_EXTRA])
                json_data = base64.b64decode(decoded).decode('utf-8') 
                extra_info = json.loads(json_data)
                return extra_info.get("tzname", "Europe/London")  # Default based on your example
            except:
                return "Unknown"

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return decoded extra information as attributes."""
        if ATTR_EXTRA not in self.coordinator.data:
            return None
        
        try:
            extra_data = self.coordinator.data[ATTR_EXTRA]
            decoded = unquote(extra_data)
            json_data = base64.b64decode(decoded).decode('utf-8')
            extra_info = json.loads(json_data)
            
            return {
                "raw_extra": extra_data,
                "decoded_extra": json_data,
                "timezone": extra_info.get("tzname", "Unknown")
            }
        except:
            return {"raw_extra": self.coordinator.data[ATTR_EXTRA]}


class TesyPositionSensor(TesySensor):
    @property
    def native_value(self):
        """Return the installation position of the water heater."""
        if ATTR_POSITION not in self.coordinator.data:
            return None
        
        position_value = self.coordinator.data[ATTR_POSITION]
        return "Vertical" if position_value == "0" else "Horizontal"
    
    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return position information as attributes."""
        if ATTR_POSITION not in self.coordinator.data:
            return None
        
        position_raw = self.coordinator.data[ATTR_POSITION]
        return {
            "position_code": position_raw,
            "description": "Installation orientation affects maximum shower settings for BelliSlimo models"
        }


class TesyMemoryUsageSensor(TesySensor):
    @property
    def native_value(self):
        """Return ESP32 free memory from system info."""
        # Try to get memory info from ESP32 discovery
        try:
            if hasattr(self.coordinator._client, 'get_esp32_system_info'):
                system_info = self.coordinator._client.get_esp32_system_info()
                for endpoint_data in system_info.values():
                    if isinstance(endpoint_data, dict):
                        # Look for common memory field names
                        memory_fields = ['free_heap', 'freeheap', 'heap_free', 'memory_free', 'free_memory']
                        for field in memory_fields:
                            if field in endpoint_data:
                                # Convert bytes to KB
                                return int(endpoint_data[field]) // 1024
            return None
        except:
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return memory information as attributes."""
        try:
            if hasattr(self.coordinator._client, 'get_esp32_system_info'):
                system_info = self.coordinator._client.get_esp32_system_info()
                memory_attrs = {}
                for endpoint, data in system_info.items():
                    if isinstance(data, dict):
                        # Extract all memory-related fields
                        memory_fields = ['free_heap', 'total_heap', 'heap_size', 'flash_size', 'flash_free']
                        for field in memory_fields:
                            if field in data:
                                memory_attrs[field] = data[field]
                return memory_attrs if memory_attrs else None
        except:
            return None


class TesyBootReasonSensor(TesySensor):
    @property
    def native_value(self):
        """Return the last boot reason."""
        try:
            if hasattr(self.coordinator._client, 'get_esp32_system_info'):
                system_info = self.coordinator._client.get_esp32_system_info()
                for endpoint_data in system_info.values():
                    if isinstance(endpoint_data, dict):
                        # Look for boot/reset reason fields
                        boot_fields = ['reset_reason', 'boot_reason', 'last_reset', 'restart_reason']
                        for field in boot_fields:
                            if field in endpoint_data:
                                return str(endpoint_data[field])
            return "Unknown"
        except:
            return "Unknown"


class TesyFirmwareBuildSensor(TesySensor):
    @property
    def native_value(self):
        """Return firmware build information."""
        try:
            if hasattr(self.coordinator._client, 'get_esp32_system_info'):
                system_info = self.coordinator._client.get_esp32_system_info()
                for endpoint_data in system_info.values():
                    if isinstance(endpoint_data, dict):
                        # Look for build date/version fields
                        build_fields = ['build_date', 'compile_date', 'firmware_date', 'build_time', 'version']
                        for field in build_fields:
                            if field in endpoint_data:
                                return str(endpoint_data[field])
                                
                        # Try to find ESP-IDF version
                        if 'esp_idf_version' in endpoint_data:
                            return f"ESP-IDF {endpoint_data['esp_idf_version']}"

            return "Unknown"
        except:
            return "Unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return firmware information as attributes."""
        try:
            if hasattr(self.coordinator._client, 'get_esp32_system_info'):
                system_info = self.coordinator._client.get_esp32_system_info()
                firmware_attrs = {}
                for endpoint, data in system_info.items():
                    if isinstance(data, dict):
                        # Extract firmware-related fields
                        fw_fields = ['sdk_version', 'esp_idf_version', 'chip_model', 'chip_cores', 'chip_revision']
                        for field in fw_fields:
                            if field in data:
                                firmware_attrs[field] = data[field]
                return firmware_attrs if firmware_attrs else None
        except:
            return None


class TesyETASensor(TesySensor):
    @property
    def native_value(self):
        """Return the ETA when target temperature will be reached."""
        try:
            countdown_minutes = int(self.coordinator.data.get(ATTR_COUNTDOWN, 0))
            if countdown_minutes > 0:
                from datetime import datetime, timedelta
                eta = datetime.now() + timedelta(minutes=countdown_minutes)
                return eta.isoformat()
            return None
        except:
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return ETA information as attributes."""
        try:
            countdown_minutes = int(self.coordinator.data.get(ATTR_COUNTDOWN, 0))
            if countdown_minutes > 0:
                from datetime import datetime, timedelta
                eta = datetime.now() + timedelta(minutes=countdown_minutes)
                return {
                    "countdown_minutes": countdown_minutes,
                    "eta_local": eta.strftime("%Y-%m-%d %H:%M:%S"),
                    "eta_relative": f"in {countdown_minutes} minutes"
                }
            return None
        except:
            return None


class TesyModeTextSensor(TesySensor):
    @property
    def native_value(self):
        """Return human-readable operation mode."""
        mode_code = self.coordinator.data.get(ATTR_MODE, "0")
        
        mode_map = {
            "0": "Performance",
            "1": "P1",
            "2": "P2", 
            "3": "P3",
            "4": "ECO",
            "5": "ECO Comfort",
            "6": "ECO Night"
        }
        
        return mode_map.get(str(mode_code), f"Unknown ({mode_code})")

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return mode information as attributes."""
        mode_code = self.coordinator.data.get(ATTR_MODE, "0")
        power_state = self.coordinator.data.get(ATTR_POWER, "0")
        
        mode_descriptions = {
            "0": "Manual temperature control",
            "1": "Program 1 - Heat in advance for scheduled time",
            "2": "Program 2 - Heat in advance for scheduled time",
            "3": "Program 3 - Thermostat mode",
            "4": "Energy saving mode",
            "5": "ECO Comfort mode",
            "6": "ECO Night mode"
        }
        
        return {
            "mode_code": mode_code,
            "description": mode_descriptions.get(str(mode_code), "Unknown mode"),
            "powered_on": power_state == "1"
        }


class TesyErrorTextSensor(TesySensor):
    @property
    def native_value(self):
        """Return human-readable error description."""
        error_code = self.coordinator.data.get(ATTR_ERROR, "00")
        
        # Error code mapping - extend as more codes are discovered
        error_map = {
            "00": "No Error",
            "01": "Temperature Sensor Error",
            "02": "Heating Element Error", 
            "03": "Communication Error",
            "04": "Power Supply Error",
            "05": "Memory Error",
            "06": "Network Error",
            "07": "Configuration Error",
            "08": "Hardware Error",
            "09": "Software Error",
            "10": "Safety Error"
        }
        
        return error_map.get(str(error_code), f"Unknown Error ({error_code})")

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return error information as attributes."""
        error_code = self.coordinator.data.get(ATTR_ERROR, "00")
        
        return {
            "error_code": error_code,
            "has_error": error_code != "00",
            "severity": "critical" if error_code != "00" else "none"
        }


class TesyStatusSnapshotSensor(TesySensor):
    @property
    def native_value(self):
        """Return overall status."""
        api_status = self.coordinator.data.get("api", "Unknown")
        return "OK" if api_status == "OK" else "Error"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return full device status as a JSON snapshot."""
        # Core operational data
        snapshot = {
            # Temperature and heating
            "temperature": self.coordinator.data.get(ATTR_CURRENT_TEMP),
            "target_temperature": self.coordinator.data.get(ATTR_TARGET_TEMP),
            "controller_target": self.coordinator.data.get(ATTR_CURRENT_TARGET_TEMP),
            "heating_active": self.coordinator.data.get(ATTR_IS_HEATING) == "1",
            
            # Mode and control
            "mode_code": self.coordinator.data.get(ATTR_MODE),
            "power_on": self.coordinator.data.get(ATTR_POWER) == "1",
            "boost_active": self.coordinator.data.get(ATTR_BOOST) == "1",
            
            # Status flags
            "child_lock": self.coordinator.data.get(ATTR_CHILD_LOCK) == "1",
            "vacation_mode": self.coordinator.data.get(ATTR_VACATION) == "1",
            "error_code": self.coordinator.data.get(ATTR_ERROR),
            
            # Timing
            "countdown_minutes": self.coordinator.data.get(ATTR_COUNTDOWN),
            "device_time": self.coordinator.data.get(ATTR_DATE),
            "uptime_seconds": self.coordinator.data.get(ATTR_UPTIME),
            
            # Network
            "wifi_ip": self.coordinator.data.get(ATTR_WIFI_IP),
            "wifi_ssid": self.coordinator.data.get(ATTR_WIFI_SSID),
            "wifi_rssi": self.coordinator.data.get(ATTR_RSSI),
            
            # Device info
            "device_id": self.coordinator.data.get(ATTR_DEVICE_ID),
            "mac_address": self.coordinator.data.get(ATTR_MAC),
            "hardware_version": self.coordinator.data.get(ATTR_HARDWARE_VERSION),
            "software_version": self.coordinator.data.get(ATTR_SOFTWARE),
            "position": self.coordinator.data.get(ATTR_POSITION),
            "max_temperature": self.coordinator.data.get(ATTR_MAX_SHOWERS),
            
            # Advanced data
            "timezone": self.coordinator.data.get(ATTR_TIMEZONE),
            "profile": self.coordinator.data.get(ATTR_PROFILE),
            "energy_counter": self.coordinator.data.get(ATTR_LONG_COUNTER),
            "reset_flag": self.coordinator.data.get(ATTR_RESET),
        }
        
        # Add programs (P1, P2, P3 for each day)
        programs = {}
        for mode in ["P1", "P2", "P3"]:
            for day in ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]:
                key = f"prg{mode}{day}"
                if key in self.coordinator.data:
                    programs[f"{mode.lower()}_{day.lower()}"] = self.coordinator.data[key]
        
        if programs:
            snapshot["programs"] = programs
        
        # Add vacation program if available
        if ATTR_PROGRAM_VACATION in self.coordinator.data:
            snapshot["vacation_program"] = self.coordinator.data[ATTR_PROGRAM_VACATION]
        
        return snapshot


class TesyDiagnosticSensor(TesySensor):
    @property
    def native_value(self):
        """Return a summary of the API response status."""
        total_fields = len(self.coordinator.data)
        api_status = self.coordinator.data.get("api", "Unknown")
        return f"OK - {total_fields} fields" if api_status == "OK" else f"Error - {api_status}"
    
    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return the full API response as attributes for debugging."""
        # Limit the response to avoid too much data in attributes
        debug_info = {
            "total_fields": len(self.coordinator.data),
            "api_status": self.coordinator.data.get("api", "Unknown"),
            "device_id": self.coordinator.data.get("id", "Unknown"),
            "software_version": self.coordinator.data.get("wsw", "Unknown"),
            "hardware_version": self.coordinator.data.get("hsw", "Unknown"),
            "mac_address": self.coordinator.data.get("MAC", "Unknown"),
            "last_update": self.coordinator.data.get("date", "Unknown"),
        }
        
        # Add key operational parameters
        operational_fields = ["tmpC", "tmpT", "tmpR", "mode", "pwr", "ht", "bst", "err"]
        for field in operational_fields:
            if field in self.coordinator.data:
                debug_info[f"current_{field}"] = self.coordinator.data[field]
        
        return debug_info


class TesyESP32DiscoverySensor(TesySensor):
    @property
    def native_value(self):
        """Return ESP32 discovery status."""
        # This sensor will trigger ESP32 discovery on update
        try:
            if hasattr(self.coordinator._client, 'probe_esp32_info'):
                discovery_info = self.coordinator._client.probe_esp32_info()
                endpoints_found = len(discovery_info.get("endpoints_discovered", []))
                return f"Found {endpoints_found} endpoints"
            else:
                return "Discovery not supported"
        except Exception as e:
            return f"Discovery failed: {str(e)}"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return ESP32 discovery information as attributes."""
        try:
            if hasattr(self.coordinator._client, 'probe_esp32_info'):
                discovery_info = self.coordinator._client.probe_esp32_info()
                
                # Summarize findings for attributes (limit size)
                attributes = {
                    "total_endpoints_found": len(discovery_info.get("endpoints_discovered", [])),
                    "system_info_available": bool(discovery_info.get("system_info")),
                    "wifi_info_available": bool(discovery_info.get("wifi_info")),
                    "debug_info_available": bool(discovery_info.get("debug_info")),
                    "firmware_info_available": bool(discovery_info.get("firmware_info")),
                }
                
                # Add first few discovered endpoints
                endpoints = discovery_info.get("endpoints_discovered", [])[:5]
                for i, endpoint in enumerate(endpoints):
                    attributes[f"endpoint_{i+1}"] = f"{endpoint['endpoint']} ({endpoint['status_code']})"
                
                # Add any system info found
                if discovery_info.get("system_info"):
                    system_info = discovery_info["system_info"]
                    for key, value in list(system_info.items())[:3]:  # Limit to first 3 items
                        if isinstance(value, (str, int, float, bool)):
                            attributes[f"system_{key}"] = value
                
                return attributes
            else:
                return {"status": "Discovery not supported for this API version"}
        except Exception as e:
            return {"error": str(e)}
