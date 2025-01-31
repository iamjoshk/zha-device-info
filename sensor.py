"""ZHA Device Info sensor platform."""

import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.zha import get_zha_gateway
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    ATTR_IEEE,
    ATTR_NWK,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_QUIRK_APPLIED,
    ATTR_POWER_SOURCE,
    ATTR_LQI,
    ATTR_RSSI,
    ATTR_LAST_SEEN,
    ATTR_AVAILABLE,
    ATTR_QUIRK_CLASS,
    ATTR_DEVICE_TYPE,
    ATTR_SIGNATURE
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up ZHA device info sensors."""
    gateway = get_zha_gateway(hass)
    if not gateway:
        _LOGGER.error("ZHA gateway not found")
        return

    entities = []
    for device in gateway.devices.values():
        entities.append(ZHADeviceInfoSensor(device))

    async_add_entities(entities)


class ZHADeviceInfoSensor(SensorEntity):
    """ZHA Device Info sensor."""

    _attr_should_poll = False
    
    def __init__(self, device) -> None:
        """Initialize the sensor."""
        self._device = device
        self._attr_unique_id = f"{DOMAIN}_{device.device_id}"  # Use device_id
        self._attr_name = f"ZHA Info {device.name}"
        
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return device specific state attributes."""
        try:
            return {
                ATTR_IEEE: str(self._device.device.ieee),  # Access through device
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
        except Exception as err:
            _LOGGER.error("Error getting attributes: %s", err)
            return {}