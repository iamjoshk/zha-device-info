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
    hass.data[DOMAIN] = {}
    device_registry = {}

    async def handle_update(call) -> None:
        """Update device info."""
        gateway: ZHAGatewayProxy = get_zha_gateway_proxy(hass)
        if not gateway:
            _LOGGER.error("ZHA gateway not found")
            return

        for device in gateway.device_proxies.values():
            zha_device: ZHADeviceProxy = async_get_zha_device_proxy(
                hass, device.device_id
            )
            
            device_info = zha_device.zha_device_info
            device_info["cluster_details"] = get_endpoint_cluster_attr_data(
                zha_device.device
            )

            if isinstance(zha_device.device.device, (CustomDevice, CustomDeviceV2)):
                signature = deepcopy(
                    zha_device.device.device.replacement 
                    if isinstance(zha_device.device.device, CustomDeviceV2)
                    else zha_device.device.device.signature
                )
                
                # Convert IDs to hex
                for ep in signature["endpoints"].values():
                    if "profile_id" in ep:
                        ep["profile_id"] = f"0x{ep['profile_id']:04x}"
                    if "device_type" in ep:
                        ep["device_type"] = f"0x{ep['device_type']:04x}"
                    if "input_clusters" in ep:
                        ep["input_clusters"] = [f"0x{c:04x}" for c in ep["input_clusters"]]
                    if "output_clusters" in ep:
                        ep["output_clusters"] = [f"0x{c:04x}" for c in ep["output_clusters"]]
                
                device_info["original_signature"] = signature

            device_registry[device.ieee] = device_info

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
