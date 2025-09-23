"""DataUpdateCoordinator for the Tesy integration."""

from __future__ import annotations

from datetime import timedelta, datetime
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

    # Standard utility methods from the REST script
    def get_minutes_to_ready(self) -> int | None:
        """Get minutes until water is ready based on CDT value."""
        if "cdt" in self.data:
            try:
                return int(self.data["cdt"])
            except (ValueError, TypeError):
                return None
        return None

    def get_ready_eta(self) -> datetime | None:
        """Calculate the timestamp when water will be ready."""
        minutes = self.get_minutes_to_ready()
        if minutes is not None and minutes > 0:
            return datetime.now() + timedelta(minutes=minutes)
        return None
    
    def get_current_step(self) -> int | None:
        """Get current shower step for Bellislimo models or temperature for other models."""
        if "tmpC" in self.data:
            try:
                return int(self.data["tmpC"])
            except (ValueError, TypeError):
                return None
        return None

    def get_target_step(self) -> int | None:
        """Get target shower step for Bellislimo models or target temperature for other models."""
        if "tmpT" in self.data:
            try:
                return int(self.data["tmpT"])
            except (ValueError, TypeError):
                return None
        return None

    def get_requested_step(self) -> int | None:
        """Get requested shower step/temperature."""
        if "tmpR" in self.data:
            try:
                return int(self.data["tmpR"])
            except (ValueError, TypeError):
                return None
        return None
    
    def get_max_step(self) -> int | None:
        """Get maximum shower step value."""
        if "tmpMX" in self.data:
            try:
                return int(self.data["tmpMX"])
            except (ValueError, TypeError):
                return None
        return None
    
    def get_mode_text(self) -> str:
        """Convert numeric mode to text representation."""
        if "mode" not in self.data:
            return "unknown"
        
        mode_map = {
            "0": "performance",
            "1": "P1", 
            "2": "P2", 
            "3": "P3",
            "4": "eco", 
            "5": "EC2", 
            "6": "EC3"
        }
        
        mode = str(self.data["mode"])
        return mode_map.get(mode, "unknown")
    
    def get_device_time(self) -> datetime | None:
        """Get the device's internal time."""
        if "date" in self.data:
            try:
                # Try to parse the date string into a datetime object
                # The format may need adjustment based on actual date format used
                date_str = self.data["date"]
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                return None
        return None
    
    def is_error_active(self) -> bool:
        """Check if there's an active error based on error code."""
        if "err" in self.data:
            return self.data["err"] != "00"
        return False
    
    def get_error_text(self) -> str:
        """Convert error code to human-readable text."""
        if "err" not in self.data:
            return "Unknown"
            
        code = str(self.data["err"])
        error_map = {"00": "OK"}
        
        return error_map.get(code, f"Unknown ({code})")
    
    def get_wifi_signal_strength(self) -> int | None:
        """Get WiFi signal strength in dBm."""
        if "wdBm" in self.data:
            try:
                return int(self.data["wdBm"])
            except (ValueError, TypeError):
                return None
        return None
