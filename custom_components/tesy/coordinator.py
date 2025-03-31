"""DataUpdateCoordinator for the Tesy integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .tesy import Tesy
from .tesy_oldapi import TesyOldApi
from .const import (
    ATTR_API,
    DOMAIN,
    UPDATE_INTERVAL,
    USE_OLD_API,
)
import logging

_LOGGER = logging.getLogger(__name__)


class TesyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Tesy Coordinator class."""

    def __init__(self, data: dict[str, Any], hass: HomeAssistant) -> None:
        """Initialize."""
        if data.get(USE_OLD_API):
            self._client = TesyOldApi(data)
        else:
            self._client = Tesy(data)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    def _validate(self) -> None:
        """Validate using Tesy API."""
        result = self._client.get_data()
        if result.get(ATTR_API) != "OK":
            raise ConnectionError
        return result

    async def async_validate_input(self) -> None:
        """Validate Tesy component."""
        return await self.hass.async_add_executor_job(self._validate)

    # Async update Data
    async def _async_update_data(self) -> dict[str, Any]:
        """Get new sensor data for Tesy component."""
        return await self.hass.async_add_executor_job(self._get_data)

    # Set target temperature in manual mode
    async def async_set_target_temperature(self, val: int) -> None:
        """Set target temperature for Tesy component."""
        return await self.hass.async_add_executor_job(
            self._client.set_target_temperature, val
        )

    # Turn power ON/OFF
    async def async_set_power(self, val: str) -> None:
        """Set power for Tesy component."""
        return await self.hass.async_add_executor_job(self._client.set_power, val)

    # Turn boost ON/OFF
    async def async_set_boost(self, val: str) -> None:
        """Set boost for Tesy component."""
        return await self.hass.async_add_executor_job(self._client.set_boost, val)

    # Turn operation mode
    async def async_set_operation_mode(self, val: str) -> None:
        """Set mode for Tesy component."""
        return await self.hass.async_add_executor_job(
            self._client.set_operation_mode, val
        )

    def _get_data(self) -> dict[str, Any]:
        """Get new sensor data using Tesy API."""
        try:
            return self._client.get_data()
        except ConnectionError as http_error:
            raise UpdateFailed from http_error

    def get_config_power(self) -> int:
        return self._client._heater_power

    async def async_discover_esp32_info(self) -> dict[str, Any]:
        """Discover additional ESP32 information."""
        if hasattr(self._client, "probe_esp32_info"):
            return await self.hass.async_add_executor_job(self._client.probe_esp32_info)
        else:
            return {"error": "ESP32 discovery not supported for this API version"}

    async def async_get_esp32_system_info(self) -> dict[str, Any]:
        """Get ESP32 system information."""
        if hasattr(self._client, "get_esp32_system_info"):
            return await self.hass.async_add_executor_job(self._client.get_esp32_system_info)
        else:
            return {"error": "ESP32 system info not supported"}

    async def async_get_esp32_wifi_info(self) -> dict[str, Any]:
        """Get ESP32 WiFi information."""
        if hasattr(self._client, "get_esp32_wifi_info"):
            return await self.hass.async_add_executor_job(self._client.get_esp32_wifi_info)
        else:
            return {"error": "ESP32 WiFi info not supported"}

    async def async_get_esp32_filesystem_info(self) -> dict[str, Any]:
        """Get ESP32 filesystem information."""
        if hasattr(self._client, "get_esp32_filesystem_info"):
            return await self.hass.async_add_executor_job(self._client.get_esp32_filesystem_info)
        else:
            return {"error": "ESP32 filesystem info not supported"}

    async def async_get_specific_endpoint(self, endpoint: str) -> dict[str, Any]:
        """Get data from a specific endpoint."""
        if hasattr(self._client, "get_specific_endpoint"):
            return await self.hass.async_add_executor_job(self._client.get_specific_endpoint, endpoint)
        else:
            return {"error": "Specific endpoint access not supported"}

    async def async_test_custom_endpoints(self, endpoints: list[str]) -> dict[str, Any]:
        """Test custom endpoints."""
        if hasattr(self._client, "test_custom_endpoints"):
            return await self.hass.async_add_executor_job(self._client.test_custom_endpoints, endpoints)
        else:
            return {"error": "Custom endpoint testing not supported"}

    async def async_scan_json_endpoints(self) -> dict[str, Any]:
        """Scan for JSON endpoints."""
        if hasattr(self._client, "scan_for_json_endpoints"):
            return await self.hass.async_add_executor_job(self._client.scan_for_json_endpoints)
        else:
            return {"error": "JSON endpoint scanning not supported"}
