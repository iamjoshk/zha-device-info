"""Config flow for ZHA Device Info integration."""
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from .const import (
    DOMAIN,
    SPLITTABLE_ATTRIBUTES,
    DEFAULT_OPTIONS,
    CONF_NAMES,
)

class ZHADeviceInfoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ZHA Device Info."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="ZHA Device Info",
                data={},
                options=user_input or DEFAULT_OPTIONS
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        conf,
                        default=DEFAULT_OPTIONS[conf],
                        description=CONF_NAMES[conf],
                    ): bool
                    for conf in SPLITTABLE_ATTRIBUTES
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow for this handler."""
        return ZHADeviceInfoOptionsFlow(config_entry)


class ZHADeviceInfoOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Don't store config_entry directly
        self.entry_id = config_entry.entry_id
        self.title = config_entry.title
        self.options = config_entry.options

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title=self.title, data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        conf,
                        default=self.options.get(conf, DEFAULT_OPTIONS[conf]),
                        description=CONF_NAMES[conf],
                    ): bool
                    for conf in SPLITTABLE_ATTRIBUTES
                }
            ),
        )
