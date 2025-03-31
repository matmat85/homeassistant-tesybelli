"""Tesy sensor component."""

from __future__ import annotations
import base64
import json
from urllib.parse import unquote

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
