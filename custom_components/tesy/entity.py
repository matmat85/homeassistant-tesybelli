"""Base entity for the Tesy integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    TESY_DEVICE_TYPES,
    ATTR_DEVICE_ID,
    ATTR_MAC,
    ATTR_BOOST,
    ATTR_SOFTWARE,
    ATTR_HARDWARE_VERSION,
    ATTR_EXTRA,
    DOMAIN,
    ATTR_API,
)
from .coordinator import TesyCoordinator

import logging
import base64
import json
from urllib.parse import unquote


_LOGGER = logging.getLogger(__name__)


class TesyEntity(CoordinatorEntity[TesyCoordinator]):
    """Defines a base Tesy entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: TesyCoordinator,
        entry: ConfigEntry,
        description: EntityDescription,
    ) -> None:
        """Initialize a Tesy entity."""
        super().__init__(coordinator)

        self.entity_description = description
        self.hass = hass
        self._entry = entry

        self._attr_unique_id = "-".join(
            [
                coordinator.data[ATTR_MAC],
                description.key,
            ]
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Tesy device."""
        device_model = "Generic"
        if self.coordinator.data[ATTR_DEVICE_ID] in TESY_DEVICE_TYPES:
            device_model = TESY_DEVICE_TYPES[self.coordinator.data[ATTR_DEVICE_ID]][
                "name"
            ]

        # Try to get custom name from extra field
        device_name = device_model
        if ATTR_EXTRA in self.coordinator.data:
            try:
                extra_data = self.coordinator.data[ATTR_EXTRA]
                decoded = unquote(extra_data)
                json_data = base64.b64decode(decoded).decode('utf-8')
                extra_info = json.loads(json_data)
                custom_name = extra_info.get("tzname", device_model)
                if custom_name and custom_name != "Unknown":
                    device_name = f"{device_model} ({custom_name})"
            except:
                pass  # Use default name if decoding fails

        # Get hardware version if available
        hw_version = self.coordinator.data.get(ATTR_HARDWARE_VERSION, 
                                              self.coordinator.data.get(ATTR_SOFTWARE, "Unknown"))

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    self.coordinator.data[ATTR_MAC],
                )
            },
            manufacturer="Tesy",
            model=device_model,
            name=device_name,
            sw_version=self.coordinator.data.get(ATTR_SOFTWARE, "Unknown"),
            hw_version=hw_version,
        )

    @property
    def is_boost_mode_on(self):
        """Return true if boost mode is on."""
        if (
            ATTR_BOOST in self.coordinator.data
            and self.coordinator.data[ATTR_BOOST] == "1"
        ):
            return True
        return False

    async def async_turn_boost_mode_on(self, **kwargs):
        """Turn on boost mode."""
        if self.coordinator.data[ATTR_BOOST] == "0":
            await self.coordinator.async_set_boost("1")

    async def async_turn_boost_mode_off(self, **kwargs):
        """Turn off boost mode."""
        if self.coordinator.data[ATTR_BOOST] == "1":
            await self.coordinator.async_set_boost("0")
