"""Tesy binary sensor component."""

from __future__ import annotations
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import TesyEntity
from .const import (
    DOMAIN,
    ATTR_IS_HEATING,
    ATTR_CHILD_LOCK,
    ATTR_VACATION,
    ATTR_BOOST,
    ATTR_POWER,
    ATTR_ERROR,
)
from .coordinator import TesyCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Tesy devices from config entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    binary_sensors = [
        TesyHeatingBinarySensor(
            hass,
            coordinator,
            entry,
            BinarySensorEntityDescription(
                key="heating",
                name="Heating",
                device_class=BinarySensorDeviceClass.HEAT,
                icon="mdi:fire",
            ),
        ),
        TesyChildLockBinarySensor(
            hass,
            coordinator,
            entry,
            BinarySensorEntityDescription(
                key="child_lock",
                name="Child Lock",
                device_class=BinarySensorDeviceClass.LOCK,
                icon="mdi:lock",
            ),
        ),
        TesyVacationModeBinarySensor(
            hass,
            coordinator,
            entry,
            BinarySensorEntityDescription(
                key="vacation_mode",
                name="Vacation Mode",
                icon="mdi:calendar-remove",
            ),
        ),
        TesyBoostModeBinarySensor(
            hass,
            coordinator,
            entry,
            BinarySensorEntityDescription(
                key="boost_mode",
                name="Boost Mode",
                icon="mdi:rocket-launch-outline",
            ),
        ),
        TesyPowerBinarySensor(
            hass,
            coordinator,
            entry,
            BinarySensorEntityDescription(
                key="power",
                name="Power",
                device_class=BinarySensorDeviceClass.POWER,
                icon="mdi:power",
            ),
        ),
        TesyErrorBinarySensor(
            hass,
            coordinator,
            entry,
            BinarySensorEntityDescription(
                key="error",
                name="Error",
                device_class=BinarySensorDeviceClass.PROBLEM,
                icon="mdi:alert-circle",
            ),
        ),
    ]
    
    async_add_entities(binary_sensors)


class TesyBinarySensor(TesyEntity, BinarySensorEntity):
    """Represents a binary sensor for a Tesy water heater controller."""

    _attr_has_entity_name = True
    _attr_should_poll = False  # Disable polling, use coordinator updates only

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: TesyCoordinator,
        entry: ConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(hass, coordinator, entry, description)

        self.entity_description = description
        self._attr_name = description.name

        if description.device_class is not None:
            self._attr_device_class = description.device_class

        if description.icon is not None:
            self._attr_icon = description.icon


class TesyHeatingBinarySensor(TesyBinarySensor):
    @property
    def is_on(self) -> bool:
        """Return true if the water heater is currently heating."""
        return self.coordinator.data.get(ATTR_IS_HEATING) == "1"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes for the heating sensor."""
        return {
            "description": "Indicates whether the heating element is currently active",
            "raw_value": self.coordinator.data.get(ATTR_IS_HEATING, "0")
        }


class TesyChildLockBinarySensor(TesyBinarySensor):
    @property
    def is_on(self) -> bool:
        """Return true if child lock is enabled."""
        return self.coordinator.data.get(ATTR_CHILD_LOCK) == "1"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes for the child lock sensor."""
        return {
            "description": "Indicates whether the device controls are locked",
            "raw_value": self.coordinator.data.get(ATTR_CHILD_LOCK, "0")
        }


class TesyVacationModeBinarySensor(TesyBinarySensor):
    @property
    def is_on(self) -> bool:
        """Return true if vacation mode is enabled."""
        return self.coordinator.data.get(ATTR_VACATION) == "1"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes for the vacation mode sensor."""
        return {
            "description": "Indicates whether vacation mode is active (reduced operation)",
            "raw_value": self.coordinator.data.get(ATTR_VACATION, "0")
        }


class TesyBoostModeBinarySensor(TesyBinarySensor):
    @property
    def is_on(self) -> bool:
        """Return true if boost mode is active."""
        return self.coordinator.data.get(ATTR_BOOST) == "1"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes for the boost mode sensor."""
        return {
            "description": "Indicates whether boost mode is active (heating to maximum temperature)",
            "raw_value": self.coordinator.data.get(ATTR_BOOST, "0")
        }


class TesyPowerBinarySensor(TesyBinarySensor):
    @property
    def is_on(self) -> bool:
        """Return true if the water heater is powered on."""
        return self.coordinator.data.get(ATTR_POWER) == "1"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes for the power sensor."""
        power_status = self.coordinator.data.get(ATTR_POWER, "0")
        return {
            "description": "Indicates whether the water heater is powered on or in antifreeze mode",
            "raw_value": power_status,
            "status_text": "On" if power_status == "1" else "Antifreeze Mode"
        }


class TesyErrorBinarySensor(TesyBinarySensor):
    @property
    def is_on(self) -> bool:
        """Return true if there's an active error."""
        error_code = self.coordinator.data.get(ATTR_ERROR, "00")
        return error_code != "00"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes for the error sensor."""
        error_code = self.coordinator.data.get(ATTR_ERROR, "00")
        return {
            "description": "Indicates whether the device has an active error condition",
            "error_code": error_code,
            "error_text": self.coordinator.get_error_text(),
            "has_error": error_code != "00"
        }
