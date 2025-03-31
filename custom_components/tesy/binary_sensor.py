"""Tesy binary sensor component."""

from __future__ import annotations

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
    ATTR_CHILD_LOCK,
    ATTR_VACATION,
    ATTR_IS_HEATING,
    ATTR_ERROR,
)
from .coordinator import TesyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Tesy binary sensors from config entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    binary_sensors = [
        TesyChildLockSensor(
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
        TesyVacationModeSensor(
            hass,
            coordinator,
            entry,
            BinarySensorEntityDescription(
                key="vacation_mode",
                name="Vacation Mode",
                icon="mdi:airplane",
            ),
        ),
        TesyHeatingSensor(
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
        TesyErrorSensor(
            hass,
            coordinator,
            entry,
            BinarySensorEntityDescription(
                key="error",
                name="Error Status",
                device_class=BinarySensorDeviceClass.PROBLEM,
                icon="mdi:alert-circle",
            ),
        ),
    ]
    
    async_add_entities(binary_sensors)


class TesyBinarySensor(TesyEntity, BinarySensorEntity):
    """Represents a binary sensor for a Tesy water heater controller."""

    _attr_has_entity_name = True
    _attr_should_poll = True

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


class TesyChildLockSensor(TesyBinarySensor):
    """Binary sensor for child lock status."""

    @property
    def is_on(self) -> bool:
        """Return true if child lock is enabled."""
        if ATTR_CHILD_LOCK not in self.coordinator.data:
            return False
        return self.coordinator.data[ATTR_CHILD_LOCK] == "1"


class TesyVacationModeSensor(TesyBinarySensor):
    """Binary sensor for vacation mode status."""

    @property
    def is_on(self) -> bool:
        """Return true if vacation mode is enabled."""
        if ATTR_VACATION not in self.coordinator.data:
            return False
        return self.coordinator.data[ATTR_VACATION] == "1"


class TesyHeatingSensor(TesyBinarySensor):
    """Binary sensor for heating status."""

    @property
    def is_on(self) -> bool:
        """Return true if heating is active."""
        if ATTR_IS_HEATING not in self.coordinator.data:
            return False
        return self.coordinator.data[ATTR_IS_HEATING] == "1"


class TesyErrorSensor(TesyBinarySensor):
    """Binary sensor for error status."""

    @property
    def is_on(self) -> bool:
        """Return true if there is an error."""
        if ATTR_ERROR not in self.coordinator.data:
            return False
        return self.coordinator.data[ATTR_ERROR] != "00"
    
    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return the error code as an attribute."""
        if ATTR_ERROR not in self.coordinator.data:
            return None
        
        error_code = self.coordinator.data[ATTR_ERROR]
        return {"error_code": error_code}
