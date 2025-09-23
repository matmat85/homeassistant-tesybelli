"""The Tesy integration."""

from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import config_validation as cv

from .coordinator import TesyCoordinator
from .const import (
    DOMAIN,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
)

PLATFORMS: list[Platform] = [
    Platform.WATER_HEATER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
]

_LOGGER = logging.getLogger(__name__)

# Service schemas
DISCOVER_ESP32_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tesy from a config entry."""
    # Merge config data with options, options take precedence
    config_data = dict(entry.data)
    if entry.options:
        config_data.update(entry.options)
    
    # Ensure update interval is set
    if CONF_UPDATE_INTERVAL not in config_data:
        config_data[CONF_UPDATE_INTERVAL] = DEFAULT_UPDATE_INTERVAL

    coordinator = TesyCoordinator(
        config_data,
        hass,
    )

    try:
        await coordinator.async_validate_input()
    except ConnectionError as connection_error:
        raise ConfigEntryAuthFailed from connection_error

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Set up update listener for options changes
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_discover_esp32(call: ServiceCall) -> None:
        """Handle ESP32 discovery service call."""
        entity_id = call.data["entity_id"]
        _LOGGER.info(f"ESP32 discovery requested for {entity_id}")
        
        # Find the coordinator for this entity
        for entry_id, coord in hass.data[DOMAIN].items():
            try:
                discovery_info = await coord.async_discover_esp32_info()
                _LOGGER.info(f"ESP32 discovery results: {discovery_info}")
                
                # Fire an event with the discovery results
                hass.bus.async_fire(
                    f"{DOMAIN}_esp32_discovery",
                    {
                        "entity_id": entity_id,
                        "discovery_info": discovery_info
                    }
                )
                break
            except Exception as e:
                _LOGGER.error(f"ESP32 discovery failed: {e}")

    async def handle_get_esp32_system_info(call: ServiceCall) -> None:
        """Handle ESP32 system info service call."""
        entity_id = call.data["entity_id"]
        
        for entry_id, coord in hass.data[DOMAIN].items():
            try:
                system_info = await coord.async_get_esp32_system_info()
                _LOGGER.info(f"ESP32 system info: {system_info}")
                
                hass.bus.async_fire(
                    f"{DOMAIN}_esp32_system_info",
                    {
                        "entity_id": entity_id,
                        "system_info": system_info
                    }
                )
                break
            except Exception as e:
                _LOGGER.error(f"ESP32 system info failed: {e}")

    async def handle_get_esp32_wifi_info(call: ServiceCall) -> None:
        """Handle ESP32 WiFi info service call."""
        entity_id = call.data["entity_id"]
        
        for entry_id, coord in hass.data[DOMAIN].items():
            try:
                wifi_info = await coord.async_get_esp32_wifi_info()
                _LOGGER.info(f"ESP32 WiFi info: {wifi_info}")
                
                hass.bus.async_fire(
                    f"{DOMAIN}_esp32_wifi_info",
                    {
                        "entity_id": entity_id,
                        "wifi_info": wifi_info
                    }
                )
                break
            except Exception as e:
                _LOGGER.error(f"ESP32 WiFi info failed: {e}")

    async def handle_get_esp32_filesystem_info(call: ServiceCall) -> None:
        """Handle ESP32 filesystem info service call."""
        entity_id = call.data["entity_id"]
        
        for entry_id, coord in hass.data[DOMAIN].items():
            try:
                fs_info = await coord.async_get_esp32_filesystem_info()
                _LOGGER.info(f"ESP32 filesystem info: {fs_info}")
                
                hass.bus.async_fire(
                    f"{DOMAIN}_esp32_filesystem_info",
                    {
                        "entity_id": entity_id,
                        "filesystem_info": fs_info
                    }
                )
                break
            except Exception as e:
                _LOGGER.error(f"ESP32 filesystem info failed: {e}")

    # Register the services
    hass.services.async_register(
        DOMAIN, "discover_esp32", handle_discover_esp32, schema=DISCOVER_ESP32_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "get_esp32_system_info", handle_get_esp32_system_info, schema=DISCOVER_ESP32_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "get_esp32_wifi_info", handle_get_esp32_wifi_info, schema=DISCOVER_ESP32_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "get_esp32_filesystem_info", handle_get_esp32_filesystem_info, schema=DISCOVER_ESP32_SCHEMA
    )

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove services
    hass.services.async_remove(DOMAIN, "discover_esp32")
    hass.services.async_remove(DOMAIN, "get_esp32_system_info")
    hass.services.async_remove(DOMAIN, "get_esp32_wifi_info")
    hass.services.async_remove(DOMAIN, "get_esp32_filesystem_info")
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
