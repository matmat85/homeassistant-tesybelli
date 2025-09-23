"""Config flow for Tesy integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import AbortFlow
import homeassistant.helpers.config_validation as cv

from .const import (
    ATTR_MAC,
    DOMAIN,
    IP_ADDRESS,
    HEATER_POWER,
    ATTR_DEVICE_ID,
    TESY_DEVICE_TYPES,
    USE_OLD_API,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    MAX_UPDATE_INTERVAL,
)
from .coordinator import TesyCoordinator

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(IP_ADDRESS): cv.string,
        vol.Required(HEATER_POWER): cv.positive_int,
        vol.Required(USE_OLD_API): cv.boolean,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_UPDATE_INTERVAL,
            default=DEFAULT_UPDATE_INTERVAL
        ): vol.All(vol.Coerce(int), vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL)),
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from USER_SCHEMA with values provided by the user.
    """

    coordinator = TesyCoordinator(data, hass)
    result = await coordinator.async_validate_input()

    title = "Tesy"

    if ATTR_DEVICE_ID in result and result[ATTR_DEVICE_ID] in TESY_DEVICE_TYPES:
        title = TESY_DEVICE_TYPES[result[ATTR_DEVICE_ID]]["name"]

    return {"title": title, "unique_id": result[ATTR_MAC]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tesy."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=USER_SCHEMA, errors={}
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)

            await self.async_set_unique_id(info["unique_id"])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=info["title"], data=user_input)
        except ConnectionError:
            errors["base"] = "cannot_connect"
        except AbortFlow as abort_flow_error:
            errors["base"] = abort_flow_error.reason
        except Exception as exception_error:  # pylint: disable=broad-except
            _LOGGER.exception(f"Unexpected exception {exception_error}")
            errors["base"] = "unknown"

        data_schema = self.add_suggested_values_to_schema(USER_SCHEMA, user_input)
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return TesyOptionsFlowHandler(config_entry)


class TesyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Tesy options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Update the coordinator with new settings
            if DOMAIN in self.hass.data and self.config_entry.entry_id in self.hass.data[DOMAIN]:
                coordinator = self.hass.data[DOMAIN][self.config_entry.entry_id]
                coordinator.update_interval_setting(user_input[CONF_UPDATE_INTERVAL])

            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL, 
            self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )

        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_UPDATE_INTERVAL,
                    default=current_interval
                ): vol.All(vol.Coerce(int), vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={
                "min_interval": str(MIN_UPDATE_INTERVAL),
                "max_interval": str(MAX_UPDATE_INTERVAL),
                "current_interval": str(current_interval),
            }
        )
