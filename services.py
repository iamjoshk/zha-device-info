import logging
from datetime import datetime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.json import save_json
from homeassistant.components import zha
from homeassistant.components.zha.helpers import async_get_zha_device_proxy

from .const import DOMAIN, SERVICE_UPDATE, SERVICE_EXPORT, SERVICE_SCHEMAS

_LOGGER = logging.getLogger(__name__)

async def async_register_services(hass: HomeAssistant) -> None:
    """Register services for ZHA Device Info."""

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
                await update_device_info(hass, device, hass.data[DOMAIN]["device_registry"])
        except Exception as dev_err:
            _LOGGER.exception("Error processing devices: %s", dev_err)

        # Update the state of each ZHA Device Info sensor
        for entity in hass.data[DOMAIN]["entities"]:
            entity.async_write_ha_state()
            _LOGGER.debug("Updated state for entity: %s", entity.name)

    async def update_device_info(hass: HomeAssistant, device, device_registry: dict) -> None:
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
            await hass.async_add_executor_job(save_json, path, hass.data[DOMAIN]["device_registry"])
            _LOGGER.info("Exported ZHA device info to %s", path)
        except Exception as err:
            _LOGGER.error("Failed to export: %s", err)

    # Register services
    async_register_admin_service(
        hass, DOMAIN, SERVICE_UPDATE, handle_update,
        schema=SERVICE_SCHEMAS[SERVICE_UPDATE]
    )
    _LOGGER.debug("Registered update service")

    async_register_admin_service(
        hass, DOMAIN, SERVICE_EXPORT, handle_export,
        schema=SERVICE_SCHEMAS[SERVICE_EXPORT]
    )
    _LOGGER.debug("Registered export service")
