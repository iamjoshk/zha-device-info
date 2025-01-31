"""ZHA Device Info sensor platform."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.components import zha
from homeassistant.components.zha.const import DATA_ZHA
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN, ATTR_IEEE, ATTR_NWK, ATTR_MANUFACTURER, ATTR_MODEL, ATTR_NAME, ATTR_QUIRK_APPLIED, ATTR_POWER_SOURCE, ATTR_LQI, ATTR_RSSI, ATTR_LAST_SEEN, ATTR_AVAILABLE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ZHA device info sensors from a config entry."""
    _LOGGER.debug("Setting up ZHA Device Info sensors")
    try:
        zha_data = hass.data.get(zha.DOMAIN)
        if not zha_data or not zha_data.gateway_proxy:
            _LOGGER.error("ZHA data or gateway proxy not found")
            return

        entities = []
        # Access devices through the ZHA gateway proxy's application controller
        for device in zha_data.gateway_proxy.application_controller.devices.values():
            if device is None:
                _LOGGER.error("Device is None, skipping")
                continue
            _LOGGER.debug("Adding ZHA Device Info sensor for device: %s", device.name)
            entity = ZHADeviceInfoSensor(device)
            entities.append(entity)
            hass.data[DOMAIN]["entities"].append(entity)
            _LOGGER.debug("Added ZHA Device Info sensor for device: %s", device.name)

        async_add_entities(entities, True)
        _LOGGER.debug("ZHA Device Info sensors setup complete")
    except Exception as err:
        _LOGGER.error("Error setting up ZHA Device Info sensors: %s", err)


class ZHADeviceInfoSensor(SensorEntity):
    """ZHA Device Info sensor."""

    _attr_should_poll = False
    
    def __init__(self, device) -> None:
        """Initialize the sensor."""
        self._device = device
        self._attr_unique_id = f"{DOMAIN}_{device.device_id}"  # Use device_id
        self._attr_name = f"ZHA Info {device.name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": device.manufacturer,
            "model": device.model,
        }
        _LOGGER.debug("Initialized ZHA Device Info sensor: %s", self._attr_name)
        
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return device specific state attributes."""
        try:
            ieee = str(self._device.device.ieee)
            _LOGGER.debug("IEEE address for device %s: %s", self._device.name, ieee)
            attributes = {
                ATTR_IEEE: ieee,  # Access through device
                ATTR_NWK: self._device.device.nwk,
                ATTR_MANUFACTURER: self._device.device.manufacturer,
                ATTR_MODEL: self._device.device.model,
                ATTR_NAME: self._device.name,
                ATTR_QUIRK_APPLIED: self._device.device.quirk_applied,
                ATTR_POWER_SOURCE: self._device.device.power_source,
                ATTR_LQI: self._device.device.lqi,
                ATTR_RSSI: self._device.device.rssi,
                ATTR_LAST_SEEN: self._device.device.last_seen.isoformat(),
                ATTR_AVAILABLE: self._device.device.available
            }
            _LOGGER.debug("Attributes for device %s: %s", self._device.name, attributes)
            return attributes
        except Exception as err:
            _LOGGER.error("Error getting attributes for device %s: %s", self._device.name, err)
            return {}

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return datetime.now().isoformat()