"""ZHA Device Info binary sensor platform."""

import logging
from typing import Any, Dict

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.device_registry import async_get
from homeassistant.components.zha.const import DOMAIN as ZHA_DOMAIN

from .const import (
    DOMAIN,
    BINARY_SENSORS,
    DEFAULT_OPTIONS,
    ATTR_QUIRK_CLASS,
    ATTR_QUIRK_APPLIED,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ZHA device info binary sensors."""
    try:
        zha_data = hass.data.get(ZHA_DOMAIN)
        if not zha_data or not zha_data.gateway_proxy:
            _LOGGER.error("ZHA gateway not found")
            return

        device_registry = async_get(hass)
        
        entities = []
        for device in zha_data.gateway_proxy.gateway.devices.values():
            if device is None:
                continue
                
            try:
                for conf, conf_data in BINARY_SENSORS.items():
                    if entry.options.get(conf, DEFAULT_OPTIONS[conf]):
                        entity = ZHADeviceBinarySensor(
                            hass, device, device_registry, conf_data
                        )
                        entities.append(entity)
                
                if entities:
                    hass.data[DOMAIN]["entities"].extend(entities)
                    
            except Exception as entity_err:
                _LOGGER.exception("Error creating binary sensor for device %s: %s", device.name, entity_err)

        async_add_entities(entities)
        
    except Exception as err:
        _LOGGER.exception("Error setting up ZHA Device Info binary sensors: %s", err)


class ZHADeviceBinarySensor(BinarySensorEntity):
    """Binary sensor for ZHA device attributes."""

    def __init__(self, hass, device, device_registry, conf_data):
        """Initialize the binary sensor."""
        self._device = device
        self._conf_data = conf_data
        device_entry = device_registry.async_get_device(
            identifiers={(ZHA_DOMAIN, str(device.ieee))},
        )
        device_name = device_entry.name_by_user if device_entry and device_entry.name_by_user else device.name
        
        self._attr_name = f"{device_name} {conf_data['name']}"
        self._attr_unique_id = f"{DOMAIN}_{device.ieee}_{conf_data['name']}"
        self.entity_id = async_generate_entity_id(
            "binary_sensor.{}",
            f"zha_device_info_{device_name.lower().replace(' ', '_')}_{conf_data['name'].lower().replace(' ', '_')}",
            hass=hass
        )
        
        self._attr_icon = conf_data["icon"]
        self._attr_device_class = conf_data.get("device_class")
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device.ieee))},
            "name": device_name,
            "manufacturer": device.manufacturer,
            "model": device.model,
        }

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        try:
            if "available" in self._conf_data["attributes"]:
                return bool(getattr(self._device, "available", False))
            elif ATTR_QUIRK_APPLIED in self._conf_data["attributes"]:
                return bool(getattr(self._device, "quirk_applied", False))
            return False
        except Exception as err:
            _LOGGER.error(
                "Error getting binary sensor state for device %s: %s",
                getattr(self._device, "name", "Unknown"),
                err,
            )
            return False

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes based on the sensor type."""
        attributes = {}
        if ATTR_QUIRK_APPLIED in self._conf_data["attributes"]:
            # Add quirk name as attribute if quirk is applied
            if self._device.quirk_applied:
                quirk = self._device.quirk_class
                if isinstance(quirk, str):
                    attributes[ATTR_QUIRK_CLASS] = quirk
                elif hasattr(quirk, "__name__"):
                    attributes[ATTR_QUIRK_CLASS] = quirk.__name__
                else:
                    attributes[ATTR_QUIRK_CLASS] = str(quirk)
        return attributes
