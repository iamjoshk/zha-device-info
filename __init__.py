import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.discovery import async_load_platform

_LOGGER = logging.getLogger(__name__)

DOMAIN = "zha_device_info"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the ZHA Device Info component."""
    _LOGGER.info("Setting up ZHA Device Info")
    hass.async_create_task(
        async_load_platform(hass, "sensor", DOMAIN, {}, config)
    )
    return True
