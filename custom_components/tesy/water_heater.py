"""Tesy water heater component."""

from typing import Any
import logging
from custom_components.tesy.coordinator import TesyCoordinator

from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_PERFORMANCE,
    WaterHeaterEntity,
    WaterHeaterEntityDescription,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_WHOLE,
    STATE_OFF,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    TESY_DEVICE_TYPES,
    ATTR_CURRENT_TEMP,
    ATTR_DEVICE_ID,
    ATTR_MAX_SHOWERS,
    ATTR_IS_HEATING,
    ATTR_MODE,
    ATTR_POWER,
    ATTR_TARGET_TEMP,
    ATTR_CURRENT_TARGET_TEMP,
    ATTR_CHILD_LOCK,
    ATTR_VACATION,
    ATTR_POSITION,
    ATTR_COUNTDOWN,
    ATTR_ERROR,
    ATTR_UPTIME,
    ATTR_RSSI,
    DOMAIN,
    TESY_MODE_P1,
    TESY_MODE_P2,
    TESY_MODE_P3,
    TESY_MODE_EC2,
    TESY_MODE_EC3,
)

from .entity import TesyEntity

_LOGGER = logging.getLogger(__name__)

OPERATION_LIST = [
    STATE_OFF,
    STATE_PERFORMANCE,
    TESY_MODE_P1,
    TESY_MODE_P2,
    TESY_MODE_P3,
    STATE_ECO,
    TESY_MODE_EC2,
    TESY_MODE_EC3,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create Tesy water heater in HASS."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            TesyWaterHeater(
                hass,
                coordinator,
                entry,
                WaterHeaterEntityDescription(
                    key="water_heater",
                    translation_key="heater",
                ),
            )
        ]
    )


class TesyWaterHeater(TesyEntity, WaterHeaterEntity):
    """Representation of an Tesy water heater."""

    _attr_operation_list = OPERATION_LIST
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_precision = PRECISION_WHOLE
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.ON_OFF
    )
    _attr_should_poll = False  # Disable polling, use coordinator updates only

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: TesyCoordinator,
        entry: ConfigEntry,
        description: Any,
    ) -> None:
        super().__init__(hass, coordinator, entry, description)

        # Default values
        self._attr_min_temp = 15
        self._attr_max_temp = 75

        if self.coordinator.data[ATTR_DEVICE_ID] in TESY_DEVICE_TYPES:
            self._attr_min_temp = TESY_DEVICE_TYPES[
                self.coordinator.data[ATTR_DEVICE_ID]
            ]["min_setpoint"]
            self._attr_max_temp = TESY_DEVICE_TYPES[
                self.coordinator.data[ATTR_DEVICE_ID]
            ]["max_setpoint"]

            # if heater only supports showers, get its maximum depending on model, position
            if (
                "use_showers"
                in TESY_DEVICE_TYPES[self.coordinator.data[ATTR_DEVICE_ID]]
                and TESY_DEVICE_TYPES[self.coordinator.data[ATTR_DEVICE_ID]][
                    "use_showers"
                ]
                == True
            ):
                if ATTR_MAX_SHOWERS in self.coordinator.data:
                    tmp_max = self.coordinator.data[ATTR_MAX_SHOWERS]
                    _LOGGER.debug("tmpMX value from device: %s (type: %s)", tmp_max, type(tmp_max))
                    try:
                        # Handle tmpMX being either string or integer
                        if tmp_max is not None:
                            self._attr_max_temp = int(tmp_max)
                            _LOGGER.debug("Set max_temp to: %s for shower-based device", self._attr_max_temp)
                    except (ValueError, TypeError) as e:
                        # If conversion fails, keep the default from device type
                        _LOGGER.warning("Failed to convert tmpMX value '%s' to integer: %s. Using default: %s", 
                                       tmp_max, e, self._attr_max_temp)
                else:
                    _LOGGER.debug("tmpMX not found in device data for shower-based device. Using default: %s", 
                                 self._attr_max_temp)
        _LOGGER.debug(
            "Initialized TesyWaterHeater: min_temp=%s, max_temp=%s",
            self._attr_min_temp,
            self._attr_max_temp,
        )

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return float(self.coordinator.data[ATTR_CURRENT_TEMP])

    @property
    def current_operation(self):
        """Return current operation."""

        if (
            ATTR_POWER not in self.coordinator.data
            or ATTR_MODE not in self.coordinator.data
        ):
            return STATE_OFF

        # if powered off
        if self.coordinator.data[ATTR_POWER] != "1":
            return STATE_OFF

        mode = self.coordinator.data[ATTR_MODE]

        if mode == "0":
            return STATE_PERFORMANCE
        if mode == "1":
            return TESY_MODE_P1
        if mode == "2":
            return TESY_MODE_P2
        if mode == "3":
            return TESY_MODE_P3
        if mode == "4":
            return STATE_ECO
        if mode == "5":
            return TESY_MODE_EC2
        if mode == "6":
            return TESY_MODE_EC3

        # Handle unknown state
        return STATE_OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        # Just in case if power is missing from json, prevent crashes
        if ATTR_POWER not in self.coordinator.data:
            return

        if self.coordinator.data[ATTR_POWER] == "1":
            if self.coordinator.data[ATTR_MODE] != STATE_PERFORMANCE:
                response = await self.coordinator.async_set_operation_mode("0")
                await self.partially_update_data_from_api(response, ATTR_MODE)

        response = await self.coordinator.async_set_target_temperature(
            kwargs.get(ATTR_TEMPERATURE)
        )
        await self.partially_update_data_from_api(response, ATTR_TARGET_TEMP)

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""

        # Just in case if power is missing from json, prevent crashes
        if ATTR_POWER not in self.coordinator.data:
            return

        if operation_mode == STATE_OFF:
            response = await self.coordinator.async_set_power("0")
            await self.partially_update_data_from_api(response, ATTR_POWER)
        else:
            if self.coordinator.data[ATTR_POWER] == "0":
                response = await self.coordinator.async_set_power("1")
                await self.partially_update_data_from_api(response, ATTR_POWER)

            if operation_mode == STATE_PERFORMANCE:
                new_mode = "0"
            if operation_mode == TESY_MODE_P1:
                new_mode = "1"
            if operation_mode == TESY_MODE_P2:
                new_mode = "2"
            if operation_mode == TESY_MODE_P3:
                new_mode = "3"
            if operation_mode == STATE_ECO:
                new_mode = "4"
            if operation_mode == TESY_MODE_EC2:
                new_mode = "4"
            if operation_mode == TESY_MODE_EC3:
                new_mode = "6"

            response = await self.coordinator.async_set_operation_mode(new_mode)
            await self.partially_update_data_from_api(response, ATTR_MODE)

    async def turn_on(self, **_kwargs: Any) -> None:
        """Turn on water heater."""
        response = await self.coordinator.async_set_power("1")
        await self.partially_update_data_from_api(response, ATTR_POWER)

    async def turn_off(self, **_kwargs: Any) -> None:
        """Turn off water heater."""
        response = await self.coordinator.async_set_power("0")
        await self.partially_update_data_from_api(response, ATTR_POWER)

    @property
    def target_temperature(self):
        """Return the target temperature."""
        # Return setpoint do
        return float(self.coordinator.data[ATTR_TARGET_TEMP])

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return the state attributes."""
        attributes = {
            "is_heating": ATTR_IS_HEATING in self.coordinator.data
            and self.coordinator.data[ATTR_IS_HEATING] == "1",
            "target_temp_step": 1,
        }

        # Add current target temperature (what the controller is actually using)
        if ATTR_CURRENT_TARGET_TEMP in self.coordinator.data:
            attributes["current_target_temperature"] = float(
                self.coordinator.data[ATTR_CURRENT_TARGET_TEMP]
            )

        # Add child lock status
        if ATTR_CHILD_LOCK in self.coordinator.data:
            attributes["child_lock"] = self.coordinator.data[ATTR_CHILD_LOCK] == "1"

        # Add vacation mode status
        if ATTR_VACATION in self.coordinator.data:
            attributes["vacation_mode"] = self.coordinator.data[ATTR_VACATION] == "1"

        # Add position (vertical/horizontal)
        if ATTR_POSITION in self.coordinator.data:
            position_value = self.coordinator.data[ATTR_POSITION]
            attributes["position"] = (
                "Vertical" if position_value == "0" else "Horizontal"
            )

        # Add countdown timer
        if ATTR_COUNTDOWN in self.coordinator.data:
            countdown_minutes = int(self.coordinator.data[ATTR_COUNTDOWN])
            if countdown_minutes > 0:
                attributes["countdown_timer_minutes"] = countdown_minutes
                attributes["countdown_timer_seconds"] = countdown_minutes * 60
                attributes["time_to_target_temperature"] = f"{countdown_minutes} minutes"

        # Add error status
        if ATTR_ERROR in self.coordinator.data:
            error_code = self.coordinator.data[ATTR_ERROR]
            attributes["error_code"] = error_code
            attributes["has_error"] = error_code != "00"

        # Add uptime information
        if ATTR_UPTIME in self.coordinator.data:
            uptime_seconds = int(self.coordinator.data[ATTR_UPTIME])
            uptime_hours = uptime_seconds // 3600
            uptime_days = uptime_hours // 24
            attributes["uptime_seconds"] = uptime_seconds
            attributes["uptime_hours"] = uptime_hours
            attributes["uptime_days"] = uptime_days

        # Add WiFi signal strength
        if ATTR_RSSI in self.coordinator.data:
            rssi = int(self.coordinator.data[ATTR_RSSI])
            attributes["wifi_signal_dbm"] = rssi
            # Convert to quality percentage (rough approximation)
            if rssi >= -50:
                signal_quality = 100
            elif rssi >= -60:
                signal_quality = 80
            elif rssi >= -70:
                signal_quality = 60
            elif rssi >= -80:
                signal_quality = 40
            elif rssi >= -90:
                signal_quality = 20
            else:
                signal_quality = 0
            attributes["wifi_signal_quality"] = f"{signal_quality}%"

        return attributes
