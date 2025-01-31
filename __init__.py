import logging
from typing import Any
from datetime import datetime

from homeassistant.components import zha
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED

from .const import DOMAIN, PLATFORMS, SERVICE_UPDATE
from .services import async_register_services

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up ZHA Device Info."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up config entry."""
    _LOGGER.debug("Setting up ZHA Device Info config entry")
    try:
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {
                "device_registry": {},
                "entities": []
            }
        _LOGGER.debug("Initialized device registry and entities list")

        await async_register_services(hass)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        # Initial update
        async def initial_update(event):
            await hass.services.async_call(DOMAIN, SERVICE_UPDATE)

        hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STARTED,
            initial_update
        )

        _LOGGER.debug("ZHA Device Info config entry setup complete")
        return True
    except Exception as err:
        _LOGGER.error("Error setting up config entry: %s", err)
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    _LOGGER.debug("Unloading ZHA Device Info config entry")
    try:
        result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        _LOGGER.debug("ZHA Device Info config entry unloaded")
        return result
    except Exception as err:
        _LOGGER.error("Error unloading config entry: %s", err)
        return False