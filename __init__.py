import logging
from homeassistant.helpers.discovery import async_load_platform

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up the ZHA Device Info component."""
    _LOGGER.info("Setting up ZHA Device Info")
    hass.async_create_task(
        async_load_platform(hass, 'sensor', 'zha_device_info', {}, config)
    )
    return True
