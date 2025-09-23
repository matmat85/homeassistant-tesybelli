"""DataUpdateCoordinator for the Tesy integration."""

from __future__ import annotations

from datetime import timedelta, datetime, timezone
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .tesy import Tesy
from .tesy_oldapi import TesyOldApi
from .const import (
    ATTR_API,
    DOMAIN,
    UPDATE_INTERVAL,
    USE_OLD_API,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
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

        # Use configurable update interval, fallback to default
        update_interval_seconds = data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        
        self._last_successful_update = None
        self._config_data = data

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
        )

    def _validate(self) -> None:
        """Validate using Tesy API."""
        result = self._client.get_data()
        if result.get(ATTR_API) != "OK":
            raise ConnectionError("API validation failed.")
        return result

    async def async_validate_input(self) -> None:
        """Validate Tesy component."""
        return await self.hass.async_add_executor_job(self._validate)

    async def _async_update_data(self) -> dict[str, Any]:
        """Get new sensor data for Tesy component."""
        try:
            data = await self.hass.async_add_executor_job(self._get_data)
            _LOGGER.debug("Fetched data: %s", data)
            # Track successful update time with timezone info
            self._last_successful_update = dt_util.utcnow()
            return data
        except Exception as e:
            _LOGGER.error("Failed to fetch data: %s", e)
            raise UpdateFailed("Failed to fetch data.")
    
    @property
    def last_successful_update(self) -> datetime | None:
        """Return the timestamp of the last successful update."""
        return self._last_successful_update
    
    @property 
    def update_interval_seconds(self) -> int:
        """Return the current update interval in seconds."""
        return int(self.update_interval.total_seconds())

    def update_interval_setting(self, new_interval: int) -> None:
        """Update the polling interval."""
        self.update_interval = timedelta(seconds=new_interval)
        self._config_data[CONF_UPDATE_INTERVAL] = new_interval
        _LOGGER.info("Update interval changed to %s seconds", new_interval)

    async def async_set_target_temperature(self, val: int) -> None:
        """Set target temperature for Tesy component."""
        return await self.hass.async_add_executor_job(
            self._client.set_target_temperature, val
        )

    async def async_set_power(self, val: str) -> None:
        """Set power for Tesy component."""
        return await self.hass.async_add_executor_job(self._client.set_power, val)

    async def async_set_boost(self, val: str) -> None:
        """Set boost for Tesy component."""
        return await self.hass.async_add_executor_job(self._client.set_boost, val)

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
            _LOGGER.error("Connection error while fetching data: %s", http_error)
            raise UpdateFailed from http_error

    def get_config_power(self) -> int:
        return self._client._heater_power

    def get_minutes_to_ready(self) -> int | None:
        """Get minutes until water is ready based on CDT value."""
        try:
            return int(self.data.get("cdt", 0))
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid CDT value: %s", self.data.get("cdt"))
            return None

    def get_ready_eta(self) -> datetime | None:
        """Calculate the timestamp when water will be ready."""
        minutes = self.get_minutes_to_ready()
        if minutes and minutes > 0:
            return datetime.now() + timedelta(minutes=minutes)
        return None

    def get_current_step(self) -> int | None:
        """Get current shower step for Bellislimo models or temperature for other models."""
        try:
            return int(self.data.get("tmpC", 0))
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid tmpC value: %s", self.data.get("tmpC"))
            return None

    def get_target_step(self) -> int | None:
        """Get target shower step for Bellislimo models or target temperature for other models."""
        try:
            return int(self.data.get("tmpT", 0))
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid tmpT value: %s", self.data.get("tmpT"))
            return None

    def get_requested_step(self) -> int | None:
        """Get requested shower step/temperature."""
        try:
            return int(self.data.get("tmpR", 0))
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid tmpR value: %s", self.data.get("tmpR"))
            return None

    def get_max_step(self) -> int | None:
        """Get maximum shower step value."""
        try:
            return int(self.data.get("tmpMX", 0))
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid tmpMX value: %s", self.data.get("tmpMX"))
            return None

    def get_mode_text(self) -> str:
        """Convert numeric mode to text representation."""
        mode_map = {
            "0": "performance",
            "1": "P1",
            "2": "P2",
            "3": "P3",
            "4": "eco",
            "5": "EC2",
            "6": "EC3",
        }
        mode = str(self.data.get("mode", "0"))
        if mode not in mode_map:
            _LOGGER.warning("Unknown mode value: %s", mode)
        return mode_map.get(mode, "unknown")

    def get_device_time(self) -> datetime | None:
        """Get the device's internal time."""
        try:
            date_str = self.data.get("date", "")
            if date_str:
                # Parse the naive datetime and make it timezone-aware (assuming UTC)
                naive_dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                return dt_util.as_utc(naive_dt)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid date value: %s", self.data.get("date"))
        return None

    def is_error_active(self) -> bool:
        """Check if there's an active error based on error code."""
        err = self.data.get("err", "00")
        if err != "00":
            _LOGGER.info("Active error detected: %s", err)
        return err != "00"

    def get_error_text(self) -> str:
        """Convert error code to human-readable text."""
        error_map = {
            "00": "OK",
        }
        code = str(self.data.get("err", "00"))
        if code not in error_map:
            _LOGGER.warning("Unknown error code: %s", code)
        return error_map.get(code, f"Unknown ({code})")

    def get_wifi_signal_strength(self) -> int | None:
        """Get WiFi signal strength in dBm."""
        try:
            return int(self.data.get("wdBm", 0))
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid wdBm value: %s", self.data.get("wdBm"))
            return None
