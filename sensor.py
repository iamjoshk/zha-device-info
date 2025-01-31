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
    ATTR_NWK,  # Add NWK attribute
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
        self._attr_unique_id = f"{DOMAIN}_{device.ieee}"
        self._attr_name = f"ZHA Info {device.name}"
        self._attr_native_value = device.nwk
        
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return device specific state attributes."""
        return {
            ATTR_IEEE: str(self._device.ieee),
            ATTR_NWK: self._device.nwk,  # Add NWK attribute
            ATTR_MANUFACTURER: self._device.manufacturer,
            ATTR_MODEL: self._device.model,
            ATTR_NAME: self._device.name,
            ATTR_QUIRK_APPLIED: self._device.quirk_applied,
            ATTR_QUIRK_CLASS: self._device.quirk_class,
            ATTR_POWER_SOURCE: self._device.power_source,
            ATTR_LQI: self._device.lqi,
            ATTR_RSSI: self._device.rssi,
            ATTR_LAST_SEEN: self._device.last_seen.isoformat(),
            ATTR_AVAILABLE: self._device.available,
            ATTR_DEVICE_TYPE: self._device.device_type,
            ATTR_SIGNATURE: self._device.signature
        }