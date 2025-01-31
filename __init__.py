import collections
import dataclasses
import logging
import os
from typing import Any
from copy import deepcopy
from datetime import datetime

import voluptuous as vol
from homeassistant.components.zha.diagnostics import get_endpoint_cluster_attr_data
from homeassistant.components.zha.helpers import (
    ZHADeviceProxy,
    ZHAGatewayProxy,
    async_get_zha_device_proxy,
    get_zha_gateway_proxy,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.json import save_json
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from slugify import slugify
from zigpy.quirks import CustomDevice
from zigpy.quirks.v2 import CustomDeviceV2

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

SERVICE_UPDATE = "update"
SERVICE_EXPORT = "export"

SERVICE_SCHEMAS = {
    SERVICE_UPDATE: vol.Schema({}),
    SERVICE_EXPORT: vol.Schema({
        vol.Optional("path"): str,
    })
}

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up ZHA Device Info."""
    _LOGGER.debug("Setting up ZHA Device Info integration")
    if DOMAIN not in config:
        _LOGGER.debug("ZHA Device Info not in config")
        return True

    hass.data[DOMAIN] = {
        "device_registry": {}
    }

    device_registry = hass.data[DOMAIN]["device_registry"]

    async def handle_update(call) -> None:
        """Update device info."""
        _LOGGER.debug("Updating ZHA device info")
        gateway: ZHAGatewayProxy = get_zha_gateway_proxy(hass)
        if not gateway:
            _LOGGER.error("ZHA gateway not found")
            return

        for device in gateway.device_proxies.values():
            try:
                zha_device = async_get_zha_device_proxy(hass, device.device_id)
                if not zha_device:
                    _LOGGER.error("ZHA device proxy not found for device %s", device.device_id)
                    continue

                last_seen = zha_device.device.last_seen
                if isinstance(last_seen, float):
                    last_seen = datetime.fromtimestamp(last_seen)

                device_info = {
                    "cluster_details": get_endpoint_cluster_attr_data(zha_device.device),
                    "ieee": str(zha_device.device.ieee),
                    "nwk": zha_device.device.nwk,
                    "manufacturer": zha_device.device.manufacturer,
                    "model": zha_device.device.model,
                    "name": zha_device.device.name,
                    "quirk_applied": zha_device.device.quirk_applied,
                    "power_source": zha_device.device.power_source,
                    "lqi": zha_device.device.lqi,
                    "rssi": zha_device.device.rssi,
                    "last_seen": last_seen.isoformat(),
                    "available": zha_device.device.available,
                }

                device_registry[zha_device.device_id] = device_info
                _LOGGER.debug("Updated info for device %s", zha_device.device_id)
                
            except Exception as err:
                _LOGGER.error("Error processing device %s: %s", device.device_id, err)

    async def handle_export(call) -> None:
        """Export device info to JSON."""
        path = call.data.get("path", hass.config.path("zha_devices.json"))
        try:
            await hass.async_add_executor_job(save_json, path, device_registry)
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

    # Initial update
    async def initial_update(event):
        await handle_update(None)

    hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_STARTED,
        initial_update
    )
    _LOGGER.debug("ZHA Device Info integration setup complete")
    return True

# Remove these if you do not have a config_flow.py
# async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Set up config entry."""
#     await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
#     return True

# async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Unload config entry."""
#     return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
