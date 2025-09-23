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
    ATTR_POWER,
    ATTR_BOOST,
    ATTR_POSITION,
    ATTR_RESET,
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
        TesyPowerBinarySensor(coordinator, entry),
        TesyHeatingBinarySensor(coordinator, entry),
        TesyBoostBinarySensor(coordinator, entry),
        TesyVacationBinarySensor(coordinator, entry),
        TesyChildLockBinarySensor(coordinator, entry),
        TesyPresenceBinarySensor(coordinator, entry),
        TesyErrorActiveBinarySensor(coordinator, entry),
        TesyResetFlagBinarySensor(coordinator, entry),
    ]
    
    async_add_entities(binary_sensors)


class TesyBinarySensor(TesyEntity, BinarySensorEntity):
    """Represents a binary sensor for a Tesy water heater controller."""

    _attr_has_entity_name = True
    _attr_should_poll = True

    def __init__(
        self,
        coordinator: TesyCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry)


class TesyPowerBinarySensor(TesyBinarySensor):
    """Binary sensor for Tesy power status."""

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("pwr") == "1"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.POWER


class TesyHeatingBinarySensor(TesyBinarySensor):
    """Binary sensor for Tesy heating status."""

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("ht") == "1"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.HEAT


class TesyBoostBinarySensor(TesyBinarySensor):
    """Binary sensor for Tesy boost status."""

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("bst") == "1"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.POWER


class TesyVacationBinarySensor(TesyBinarySensor):
    """Binary sensor for Tesy vacation mode."""

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("vac") == "1"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.PRESENCE


class TesyChildLockBinarySensor(TesyBinarySensor):
    """Binary sensor for Tesy child lock."""

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("lck") == "1"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.LOCK


class TesyPresenceBinarySensor(TesyBinarySensor):
    """Binary sensor for Tesy presence."""

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("psn") == "1"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.PRESENCE


class TesyErrorActiveBinarySensor(TesyBinarySensor):
    """Binary sensor for Tesy error active status."""

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("err") != "00"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.PROBLEM


class TesyResetFlagBinarySensor(TesyBinarySensor):
    """Binary sensor for Tesy reset flag."""

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("reset") == "1"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.PROBLEM
