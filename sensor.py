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
from homeassistant.helpers.entity import async_generate_entity_id

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
        _LOGGER.debug("Available domains in hass.data: %s", list(hass.data.keys()))
        zha_data = hass.data.get(zha.DOMAIN)
        _LOGGER.debug("ZHA data type: %s", type(zha_data))
        _LOGGER.debug("ZHA data attributes: %s", dir(zha_data))
        
        if not zha_data:
            _LOGGER.error("ZHA data not found in hass.data")
            return
            
        _LOGGER.debug("ZHA gateway_proxy type: %s", type(zha_data.gateway_proxy))
        if not zha_data.gateway_proxy:
            _LOGGER.error("ZHA gateway proxy not found in zha_data")
            return

        _LOGGER.debug("ZHA gateway type: %s", type(zha_data.gateway_proxy.gateway))
        _LOGGER.debug("Available gateway attributes: %s", dir(zha_data.gateway_proxy.gateway))
        
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {"entities": []}
        
        entities = []
        for device in zha_data.gateway_proxy.gateway.devices.values():
            if device is None:
                _LOGGER.error("Device is None, skipping")
                continue
            _LOGGER.debug("Device type: %s", type(device))
            _LOGGER.debug("Device attributes: %s", dir(device))
            _LOGGER.debug("Adding ZHA Device Info sensor for device: %s", device.name)
            
            try:
                entity = ZHADeviceInfoSensor(hass, device)
                entities.append(entity)
                hass.data[DOMAIN]["entities"].append(entity)
                _LOGGER.debug("Added ZHA Device Info sensor for device: %s", device.name)
            except Exception as entity_err:
                _LOGGER.exception("Error creating sensor for device %s: %s", device.name, entity_err)

        async_add_entities(entities, True)
        _LOGGER.debug("ZHA Device Info sensors setup complete")
    except Exception as err:
        _LOGGER.exception("Error setting up ZHA Device Info sensors: %s", err, exc_info=True)


class ZHADeviceInfoSensor(SensorEntity):
    """ZHA Device Info sensor."""

    _attr_should_poll = False
    
    def __init__(self, hass: HomeAssistant, device) -> None:
        """Initialize the sensor."""
        self._device = device
        device_name = device.name_by_user or device.name
        self._attr_name = f"ZHA Device Info {device_name}"
        self._attr_unique_id = f"{DOMAIN}_{device.ieee}"  # Use ieee
        self.entity_id = async_generate_entity_id("sensor.{}", self._attr_name.lower().replace(" ", "_"), hass=hass)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device.ieee))},
            "name": device_name,
            "manufacturer": device.manufacturer,
            "model": device.model,
        }
        _LOGGER.debug("Initialized ZHA Device Info sensor: %s", self._attr_name)
        
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return device specific state attributes."""
        try:
            ieee = str(self._device.ieee)
            _LOGGER.debug("IEEE address for device %s: %s", self._device.name, ieee)
            last_seen = self._device.last_seen
            if isinstance(last_seen, float):
                last_seen = datetime.fromtimestamp(last_seen)
            nwk_hex = f"0x{self._device.nwk:04x}"
            attributes = {
                ATTR_IEEE: ieee,  # Access through device
                ATTR_NWK: nwk_hex,
                ATTR_MANUFACTURER: self._device.manufacturer,
                ATTR_MODEL: self._device.model,
                ATTR_NAME: self._device.name,
                ATTR_QUIRK_APPLIED: self._device.quirk_applied,
                ATTR_POWER_SOURCE: self._device.power_source,
                ATTR_LQI: self._device.lqi,
                ATTR_RSSI: self._device.rssi,
                ATTR_LAST_SEEN: last_seen.isoformat(),
                ATTR_AVAILABLE: self._device.available
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