"""Config flow for .be Domain Checker integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
from .__init__ import check_be_domain

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DOMAIN): str,
        vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for .be Domain Checker."""

    VERSION = 1

    @staticmethod
    @core.callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return BeDomainOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            domain = user_input[CONF_DOMAIN].strip().lower()
            if not domain.endswith(".be"):
                domain = f"{domain}.be"
            
            user_input[CONF_DOMAIN] = domain

            # Check if domain is already configured
            await self.async_set_unique_id(domain)
            self._abort_if_unique_id_configured()

            try:
                # Test the connection/whois lookup
                await self.hass.async_add_executor_job(check_be_domain, domain)
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=domain,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class BeDomainOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for .be Domain Checker."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Build schema using the current options or the initial data fallback
        current_interval = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL,
            self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
        )
        
        schema = vol.Schema(
            {
                vol.Required(CONF_UPDATE_INTERVAL, default=current_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=1)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
