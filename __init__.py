import collections
import dataclasses
import logging
import os
from typing import Any
from copy import deepcopy

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
    if DOMAIN not in config:
        return True

    hass.data[DOMAIN] = {
        "device_registry": {}
    }

    device_registry = hass.data[DOMAIN]["device_registry"]

    async def handle_update(call) -> None:
        """Update device info."""
        gateway: ZHAGatewayProxy = get_zha_gateway_proxy(hass)
        if not gateway:
            _LOGGER.error("ZHA gateway not found")
            return

        device_registry = hass.data[DOMAIN]["device_registry"]

        for device in gateway.device_proxies.values():
            try:
                zha_device = async_get_zha_device_proxy(hass, device.device_id)
                if not zha_device:
                    continue

                device_info = zha_device.device.zha_device_info
                device_info["cluster_details"] = get_endpoint_cluster_attr_data(
                    zha_device.device
                )

                # Use device_id instead of ieee
                device_registry[zha_device.device_id] = device_info
                
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
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, lambda _: handle_update(None))

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
