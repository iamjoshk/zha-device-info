import logging
import os
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.json import save_json
from homeassistant.components.zha.core.helpers import get_zha_gateway
from homeassistant.components.zha.core.device import ZHADevice
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
import voluptuous as vol

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = f"{DOMAIN}.devices"
STORAGE_VERSION = 1

SERVICE_UPDATE = "update"
SERVICE_EXPORT = "export"

SERVICE_SCHEMAS = {
    SERVICE_UPDATE: vol.Schema({}),
    SERVICE_EXPORT: vol.Schema({
        vol.Optional("path"): str,
    })
}

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the ZHA Device Info integration."""
    hass.data[DOMAIN] = {}
    
    device_registry = {}

    async def handle_update(call) -> None:
        """Update device info from ZHA."""
        gateway = get_zha_gateway(hass)
        if not gateway:
            _LOGGER.error("ZHA gateway not found")
            return

        for device in gateway.devices.values():
            if not isinstance(device, ZHADevice):
                continue
                
            device_info = {
                "ieee": str(device.ieee),
                "nwk": device.nwk,
                "manufacturer": device.manufacturer,
                "model": device.model,
                "name": device.name,
                "quirk_applied": device.quirk_applied,
                "endpoints": {}
            }
            
            for endpoint_id, endpoint in device.endpoints.items():
                if endpoint_id != 0:
                    device_info["endpoints"][endpoint_id] = {
                        "profile_id": endpoint.profile_id,
                        "device_type": endpoint.device_type,
                        "in_clusters": list(endpoint.in_clusters.keys()),
                        "out_clusters": list(endpoint.out_clusters.keys())
                    }
            
            device_registry[device.ieee] = device_info

    async def handle_export(call) -> None:
        """Export device info to JSON."""
        path = call.data.get("path", hass.config.path("zha_devices.json"))
        try:
            await hass.async_add_executor_job(
                save_json, path, device_registry
            )
            _LOGGER.info("Exported ZHA device info to %s", path)
        except Exception as err:
            _LOGGER.error("Failed to export: %s", err)

    # Register services
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE, handle_update, 
        schema=SERVICE_SCHEMAS[SERVICE_UPDATE]
    )
    hass.services.async_register(
        DOMAIN, SERVICE_EXPORT, handle_export,
        schema=SERVICE_SCHEMAS[SERVICE_EXPORT]
    )

    # Initial update when HA starts
    async def startup_update(_):
        """Update device info when HA starts."""
        await handle_update(None)
    
    hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_STARTED, startup_update
    )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
