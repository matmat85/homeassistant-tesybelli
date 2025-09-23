"""Tesy sensor component."""

from __future__ import annotations
import base64
import json
from urllib.parse import unquote
from typing import Any
from datetime import datetime

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
    ATTR_TARGET_TEMP,
    ATTR_CURRENT_TARGET_TEMP,
    ATTR_MAX_SHOWERS,
    ATTR_MODE,
    ATTR_POWER,
    ATTR_BOOST,
    ATTR_IS_HEATING,
    ATTR_DEVICE_ID,
    ATTR_SOFTWARE,
    ATTR_MAC,
    ATTR_DATE,
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
        # New sensors from REST script
        TesyMinutesToReadySensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="minutes_to_ready",
                name="Minutes To Ready",
                device_class=None,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement=UnitOfTime.MINUTES,
                icon="mdi:timer",
            ),
            None,
            None,
        ),
        TesyReadyETASensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="ready_eta",
                name="Ready ETA",
                device_class=SensorDeviceClass.TIMESTAMP,
                icon="mdi:clock-time-five-outline",
            ),
            None,
            None,
        ),
        TesyCurrentStepSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="current_step",
                name="Current Step",
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:stairs",
            ),
            None,
            None,
        ),
        TesyTargetStepSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="target_step",
                name="Target Step",
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:target",
            ),
            None,
            None,
        ),
        TesyRequestedStepSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="requested_step",
                name="Requested Step",
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:run",
            ),
            None,
            None,
        ),
        TesyModeCodeSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="mode_code",
                name="Mode Code",
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:tune-variant",
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
                name="Mode",
                icon="mdi:water-boiler",
            ),
            None,
            None,
        ),
        TesyDeviceTimeSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="device_time",
                name="Device Time",
                device_class=SensorDeviceClass.TIMESTAMP,
                icon="mdi:clock",
            ),
            None,
            None,
        ),
        TesyWarmupCounterSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="warmup_counter",
                name="Warmup Counter",
                state_class=SensorStateClass.TOTAL,
                icon="mdi:counter",
            ),
            None,
            None,
        ),
        TesyMaxStepSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="max_step",
                name="Max Step",
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:numeric-4-box-outline",
            ),
            None,
            None,
        ),
        TesyErrorCodeTextSensor(
            hass,
            coordinator,
            entry,
            SensorEntityDescription(
                key="error_code_text",
                name="Error Code Text",
                icon="mdi:alert-circle",
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
                name="Status Snapshot",
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
                name="Diagnostic Status",
                icon="mdi:stethoscope",
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

        self.description: description
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


# New sensors from the REST script
class TesyMinutesToReadySensor(TesySensor):
    @property
    def native_value(self):
        """Return the minutes until ready value."""
        return self.coordinator.get_minutes_to_ready()


class TesyReadyETASensor(TesySensor):
    @property
    def native_value(self):
        """Return the estimated timestamp when water will be ready."""
        return self.coordinator.get_ready_eta()
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return ETA details as attributes."""
        minutes = self.coordinator.get_minutes_to_ready()
        if minutes is None:
            return None
            
        return {
            "minutes_remaining": minutes,
            "seconds_remaining": minutes * 60 if minutes is not None else None
        }


class TesyCurrentStepSensor(TesySensor):
    @property
    def native_value(self):
        """Return the current step or temperature value."""
        # Use the new mapped entity for current step
        current_step = self.hass.states.get("sensor.tesy_current_step_mapped")
        if current_step is None or current_step.state in ["unknown", "unavailable", ""]:
            return None
        return int(current_step.state)


class TesyTargetStepSensor(TesySensor):
    @property
    def native_value(self):
        """Return the target step or temperature value."""
        # Use the new mapped entity for target step
        target_step = self.hass.states.get("sensor.tesy_target_step_mapped")
        if target_step is None or target_step.state in ["unknown", "unavailable", ""]:
            return None
        return int(target_step.state)


class TesyRequestedStepSensor(TesySensor):
    @property
    def native_value(self):
        """Return the requested step or temperature value."""
        # Use the new mapped entity for requested step
        requested_step = self.hass.states.get("sensor.tesy_requested_step_mapped")
        if requested_step is None or requested_step.state in ["unknown", "unavailable", ""]:
            return None
        return int(requested_step.state)


class TesyModeCodeSensor(TesySensor):
    @property
    def native_value(self):
        """Return the numeric mode code."""
        if ATTR_MODE not in self.coordinator.data:
            return None
        return int(self.coordinator.data[ATTR_MODE])


class TesyModeTextSensor(TesySensor):
    @property
    def native_value(self):
        """Return the text representation of the mode."""
        # Use the new mapped entity for mode
        mode = self.hass.states.get("sensor.tesy_mode_mapped")
        if mode is None or mode.state in ["unknown", "unavailable", ""]:
            return None
        return mode.state

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return mode information as attributes."""
        mode = self.hass.states.get("sensor.tesy_mode_mapped")
        if mode is None or mode.state in ["unknown", "unavailable", ""]:
            return None

        mode_map = {
            "0": "Performance/Manual mode",
            "1": "Program 1 (P1)",
            "2": "Program 2 (P2)",
            "3": "Program 3 (P3)",
            "4": "ECO mode",
            "5": "ECO Comfort (EC2)",
            "6": "ECO Night (EC3)"
        }

        return {
            "mode_code": mode.state,
            "description": mode_map.get(mode.state, "Unknown mode")
        }


class TesyDeviceTimeSensor(TesySensor):
    @property
    def native_value(self):
        """Return the device's internal time."""
        return self.coordinator.get_device_time()


class TesyWarmupCounterSensor(TesySensor):
    @property
    def native_value(self):
        """Return the device warmup counter."""
        if "wup" in self.coordinator.data:
            try:
                return int(self.coordinator.data["wup"])
            except (ValueError, TypeError):
                return None
        return None


class TesyMaxStepSensor(TesySensor):
    @property
    def native_value(self):
        """Return the maximum number of steps/showers."""
        return self.coordinator.get_max_step()
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return information about the maximum step setting."""
        max_step = self.coordinator.get_max_step()
        if max_step is None:
            return None
            
        return {
            "max_value": max_step,
            "description": "Maximum number of showers for BelliSlimo models, depends on device orientation and capacity"
        }


class TesyErrorCodeTextSensor(TesySensor):
    @property
    def native_value(self):
        """Return the human-readable error message."""
        return self.coordinator.get_error_text()
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return error code details as attributes."""
        if ATTR_ERROR not in self.coordinator.data:
            return None
            
        error_code = self.coordinator.data[ATTR_ERROR]
        return {
            "raw_code": error_code,
            "is_error_active": error_code != "00"
        }


class TesyStatusSnapshotSensor(TesySensor):
    @property
    def native_value(self):
        """Always return OK for the snapshot sensor."""
        return "OK"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the full snapshot of device state as attributes."""
        # List of important keys to include in the snapshot
        key_fields = [
            'tz', 'wsw', 'prfl', 'extr', 'id', 'date', 'wtstp', 'wup', 'hsw', 'tmpMX', 
            'reset', 'err', 'tmpT', 'tmpR', 'mode', 'lck', 'bst', 'vac', 'pwr', 'ht', 
            'psn', 'tmpC', 'cdt', 'PICTime', 'prgVac', 'wIP', 'wSSID', 'wdBm', 'MAC', 'api'
        ]
        
        # Program schedule fields for each day
        program_fields = []
        for program in ['prgP1', 'prgP2', 'prgP3']:
            for day in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']:
                program_fields.append(f"{program}{day}")
                
        # Combine all fields
        all_fields = key_fields + program_fields
        
        # Create snapshot with available data
        snapshot = {}
        for field in all_fields:
            if field in self.coordinator.data:
                snapshot[field] = self.coordinator.data[field]
                
        return snapshot
