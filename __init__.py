import logging
from typing import Any
from datetime import datetime

import voluptuous as vol
from homeassistant.components import zha
from homeassistant.components.zha.const import DATA_ZHA
from homeassistant.components.zha.helpers import (
    ZHADeviceProxy,
    async_get_zha_device_proxy,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.json import save_json
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED

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

    try:
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {
                "device_registry": {},
                "entities": []
            }
        _LOGGER.debug("Initialized device registry and entities list")

        device_registry = hass.data[DOMAIN]["device_registry"]

        async def handle_update(call) -> None:
            """Update device info."""
            _LOGGER.debug("Updating ZHA device info")
            _LOGGER.debug("Available domains in hass.data: %s", list(hass.data.keys()))
            zha_data = hass.data.get(zha.DOMAIN)
            _LOGGER.debug("ZHA data type: %s", type(zha_data))
            
            if not zha_data:
                _LOGGER.error("ZHA data not found in hass.data")
                return
                
            _LOGGER.debug("ZHA gateway_proxy type: %s", type(zha_data.gateway_proxy))
            if not zha_data.gateway_proxy:
                _LOGGER.error("ZHA gateway proxy not found in zha_data")
                return

            _LOGGER.debug("ZHA gateway type: %s", type(zha_data.gateway_proxy.gateway))
            try:
                for device in zha_data.gateway_proxy.gateway.devices.values():
                    if device is None:
                        _LOGGER.error("Device is None, skipping")
                        continue
                    _LOGGER.debug("Processing device type: %s", type(device))
                    _LOGGER.debug("Device attributes: %s", dir(device))
                    await update_device_info(hass, device, device_registry)
            except Exception as dev_err:
                _LOGGER.exception("Error processing devices: %s", dev_err)

            # Update the state of each ZHA Device Info sensor
            for entity in hass.data[DOMAIN]["entities"]:
                entity.async_write_ha_state()
                _LOGGER.debug("Updated state for entity: %s", entity.name)

        async def update_device_info(hass: HomeAssistant, device: ZHADeviceProxy, device_registry: dict) -> None:
            """Helper function to update a single device's info."""
            try:
                zha_device = async_get_zha_device_proxy(hass, device.ieee)
                if not zha_device:
                    _LOGGER.error("ZHA device proxy not found for device %s", device.ieee)
                    return

                last_seen = zha_device.device.last_seen
                if isinstance(last_seen, float):
                    last_seen = datetime.fromtimestamp(last_seen)
                nwk_hex = f"0x{zha_device.device.nwk:04x}"
                device_info = {
                    "ieee": str(zha_device.device.ieee),
                    "nwk": nwk_hex,
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

                device_registry[str(zha_device.device.ieee)] = device_info
                _LOGGER.debug("Updated info for device %s", zha_device.device.ieee)
                
            except Exception as err:
                _LOGGER.error("Error processing device %s: %s", device.ieee, err)

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
        _LOGGER.debug("Registered update service")

        hass.services.async_register(
            DOMAIN, SERVICE_EXPORT, handle_export,
            schema=SERVICE_SCHEMAS[SERVICE_EXPORT]
        )
        _LOGGER.debug("Registered export service")

        # Initial update
        async def initial_update(event):
            await handle_update(None)

        hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STARTED,
            initial_update
        )
        _LOGGER.debug("ZHA Device Info integration setup complete")
        return True

    except Exception as err:
        _LOGGER.error("Error during setup: %s", err)
        return False

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up config entry."""
    _LOGGER.debug("Setting up ZHA Device Info config entry")
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
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