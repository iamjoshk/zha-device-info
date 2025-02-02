"""ZHA Device Info sensor platform."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime
import time

from homeassistant.components.sensor import SensorEntity
from homeassistant.util import dt as dt_util
from homeassistant.components import zha
from homeassistant.components.zha.const import DOMAIN as ZHA_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.device_registry import async_get
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    PERCENTAGE,
)

from .const import (
    DOMAIN, ATTR_DEVICE_TYPE, ATTR_IEEE, ATTR_NWK, 
    ATTR_MANUFACTURER, ATTR_MODEL, 
    ATTR_NAME, ATTR_QUIRK_APPLIED, 
    ATTR_QUIRK_CLASS, ATTR_POWER_SOURCE, 
    ATTR_LQI, ATTR_RSSI, ATTR_LAST_SEEN, 
    ATTR_AVAILABLE, SPLITTABLE_ATTRIBUTES,
    DEFAULT_OPTIONS
)


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ZHA device info sensors from a config entry."""
    _LOGGER.debug("Setting up ZHA Device Info sensors")
    try:
        zha_data = hass.data.get(ZHA_DOMAIN)
        if not zha_data or not zha_data.gateway_proxy:
            _LOGGER.error("ZHA gateway not found")
            return

        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {"entities": []}
        
        device_registry = async_get(hass)
        
        entities = []
        for device in zha_data.gateway_proxy.gateway.devices.values():
            if device is None:
                continue
                
            try:
                # Add main sensor
                main_entity = ZHADeviceInfoSensor(hass, device, device_registry)
                entities.append(main_entity)
                
                # Add split attribute sensors based on config
                for conf, conf_data in SPLITTABLE_ATTRIBUTES.items():
                    if entry.options.get(conf, DEFAULT_OPTIONS[conf]):
                        entity = ZHADeviceAttributeSensor(
                            hass, device, device_registry, conf_data
                        )
                        entities.append(entity)
                        
                hass.data[DOMAIN]["entities"].extend(entities)
                
            except Exception as entity_err:
                _LOGGER.exception("Error creating sensor for device %s: %s", device.name, entity_err)

        async_add_entities(entities, True)
        _LOGGER.debug("ZHA Device Info sensors setup complete")
    except Exception as err:
        _LOGGER.exception("Error setting up ZHA Device Info sensors: %s", err)


class ZHADeviceInfoSensor(SensorEntity):
    """ZHA Device Info sensor."""

    _attr_should_poll = False
    
    def __init__(self, hass: HomeAssistant, device, device_registry) -> None:
        """Initialize the sensor."""
        self._device = device
        # Look up device using ZHA domain identifiers
        device_entry = device_registry.async_get_device(
            identifiers={(ZHA_DOMAIN, str(device.ieee))},
        )
        _LOGGER.debug("Device entry from registry: %s", device_entry)
        _LOGGER.debug("Device entry name_by_user: %s", device_entry.name_by_user if device_entry else None)
        
        # Use name_by_user if available, otherwise use device name
        device_name = device_entry.name_by_user if device_entry and device_entry.name_by_user else device.name
        _LOGGER.debug("Using name for device %s: %s", device.ieee, device_name)
        
        # Simplified friendly name
        self._attr_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{device.ieee}"
        # Keep the full entity_id format
        self.entity_id = async_generate_entity_id(
            "sensor.{}",
            f"zha_device_info_{device_name.lower().replace(' ', '_')}",
            hass=hass
        )
        
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
                ATTR_IEEE: ieee,
                ATTR_NWK: nwk_hex,
                ATTR_MANUFACTURER: self._device.manufacturer,
                ATTR_MODEL: self._device.model,
                ATTR_NAME: self._device.name,
                ATTR_QUIRK_APPLIED: self._device.quirk_applied,
                ATTR_POWER_SOURCE: self._device.power_source,
                ATTR_LQI: self._device.lqi,
                ATTR_RSSI: self._device.rssi,
                ATTR_LAST_SEEN: last_seen.isoformat(),
                ATTR_AVAILABLE: self._device.available,
                ATTR_DEVICE_TYPE: self._device.device_type,  # Add device type
            }

            # Add quirk_class if quirk is applied
            if self._device.quirk_applied:
                quirk = self._device.quirk_class
                if isinstance(quirk, str):
                    attributes["quirk_class"] = quirk
                elif hasattr(quirk, "__name__"):
                    attributes["quirk_class"] = quirk.__name__
                else:
                    attributes["quirk_class"] = str(quirk)

            _LOGGER.debug("Attributes for device %s: %s", self._device.name, attributes)
            return attributes
        except Exception as err:
            _LOGGER.error("Error getting attributes for device %s: %s", self._device.name, err)
            return {}

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return str(self._device.ieee)


class ZHADeviceAttributeSensor(SensorEntity):
    """Representation of a ZHA Device attribute sensor."""

    def __init__(self, hass, device, device_registry, conf_data):
        """Initialize the sensor."""
        self._device = device
        self._conf_data = conf_data
        device_entry = device_registry.async_get_device(
            identifiers={(ZHA_DOMAIN, str(device.ieee))},
        )
        device_name = device_entry.name_by_user if device_entry and device_entry.name_by_user else device.name
        
        # Simplified friendly name
        self._attr_name = f"{device_name} {conf_data['name']}"
        self._attr_unique_id = f"{DOMAIN}_{device.ieee}_{conf_data['name']}"
        # Keep the full entity_id format
        self.entity_id = async_generate_entity_id(
            "sensor.{}",
            f"zha_device_info_{device_name.lower().replace(' ', '_')}_{conf_data['name'].lower().replace(' ', '_')}",
            hass=hass
        )
        
        self._attr_icon = conf_data["icon"]
        self._attr_device_class = conf_data.get("device_class")
        self._attr_state_class = conf_data.get("state_class")
        
        # Only set unit of measurement for numeric sensors
        if "signal_strength" in conf_data["name"].lower():
            self._attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
        elif "lqi" in conf_data["attributes"]:
            self._attr_native_unit_of_measurement = PERCENTAGE
        
        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device.ieee))},
            "name": device_name,
            "manufacturer": device.manufacturer,
            "model": device.model,
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            if not self._device:
                _LOGGER.debug("Device is None")
                return None

            # Ensure device has necessary attributes before accessing them
            if "rssi" in self._conf_data["attributes"]:
                return getattr(self._device, "rssi", None)
            elif "lqi" in self._conf_data["attributes"]:
                return getattr(self._device, "lqi", None)
            elif "last_seen" in self._conf_data["attributes"]:
                last_seen = getattr(self._device, "last_seen", None)
                if isinstance(last_seen, float):
                    return dt_util.as_local(datetime.fromtimestamp(last_seen))
                return last_seen
            elif "available" in self._conf_data["attributes"]:
                return getattr(self._device, "available", None)
            elif "power_source" in self._conf_data["attributes"]:
                return str(getattr(self._device, "power_source", None))
            elif ATTR_NWK in self._conf_data["attributes"]:
                nwk = getattr(self._device, "nwk", None)
                return f"0x{nwk:04x}" if nwk is not None else None
            elif ATTR_QUIRK_APPLIED in self._conf_data["attributes"]:
                return getattr(self._device, "quirk_applied", False)
            elif ATTR_DEVICE_TYPE in self._conf_data["attributes"]:
                device_type = getattr(self._device, "device_type", None)
                return str(device_type) if device_type is not None else None
            return None

        except Exception as err:
            _LOGGER.error(
                "Error getting native value for device %s: %s",
                getattr(self._device, "name", "Unknown"),
                err,
            )
            return None

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