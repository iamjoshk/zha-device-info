"""Constants for ZHA Device Info integration."""

import voluptuous as vol

DOMAIN = "zha_device_info"
PLATFORMS = ["sensor"]

# Service names
SERVICE_UPDATE = "update"
SERVICE_EXPORT = "export"

# Service schemas
SERVICE_SCHEMAS = {
    SERVICE_UPDATE: vol.Schema({}),
    SERVICE_EXPORT: vol.Schema({
        vol.Optional("path"): str,
    })
}

# Attributes
ATTR_IEEE = "ieee"
ATTR_NWK = "nwk"
ATTR_MANUFACTURER = "manufacturer"
ATTR_MODEL = "model"
ATTR_NAME = "name"
ATTR_QUIRK_APPLIED = "quirk_applied"
ATTR_QUIRK_CLASS = "quirk_class"
ATTR_POWER_SOURCE = "power_source"
ATTR_LQI = "lqi"
ATTR_RSSI = "rssi"
ATTR_LAST_SEEN = "last_seen"
ATTR_AVAILABLE = "available"
ATTR_DEVICE_TYPE = "device_type"
ATTR_SIGNATURE = "signature"
ATTR_CLUSTER_DETAILS = "cluster_details"
ATTR_ENDPOINTS = "endpoints"

# Splittable Attributes Configuration
CONF_SPLIT_SIGNAL_STRENGTH = "split_signal_strength"
CONF_SPLIT_LAST_SEEN = "split_last_seen"
CONF_SPLIT_AVAILABILITY = "split_availability"
CONF_SPLIT_POWER = "split_power"
CONF_SPLIT_NWK = "split_nwk"  # New
CONF_SPLIT_QUIRK = "split_quirk"  # New

SPLITTABLE_ATTRIBUTES = {
    CONF_SPLIT_SIGNAL_STRENGTH: {
        "name": "Signal Strength",
        "attributes": [ATTR_LQI, ATTR_RSSI],
        "icon": "mdi:signal",
        "device_class": "signal_strength",
    },
    CONF_SPLIT_LAST_SEEN: {
        "name": "Last Seen",
        "attributes": [ATTR_LAST_SEEN],
        "icon": "mdi:clock-outline",
        "device_class": "timestamp",
    },
    CONF_SPLIT_AVAILABILITY: {
        "name": "Availability",
        "attributes": [ATTR_AVAILABLE],
        "icon": "mdi:check-network-outline",
        "device_class": "connectivity",
    },
    CONF_SPLIT_POWER: {
        "name": "Power Source",
        "attributes": [ATTR_POWER_SOURCE],
        "icon": "mdi:battery",
        "device_class": None,  # Remove power device_class
        "state_class": None,
    },
    CONF_SPLIT_NWK: {
        "name": "Network Address",
        "attributes": [ATTR_NWK],
        "icon": "mdi:identifier",
        "device_class": None,
    },
    CONF_SPLIT_QUIRK: {
        "name": "Quirk Info",
        "attributes": [ATTR_QUIRK_APPLIED, ATTR_QUIRK_CLASS],
        "icon": "mdi:puzzle",
        "device_class": None,
    },
}

# Default configuration
DEFAULT_OPTIONS = {
    CONF_SPLIT_SIGNAL_STRENGTH: False,
    CONF_SPLIT_LAST_SEEN: False,
    CONF_SPLIT_AVAILABILITY: False,
    CONF_SPLIT_POWER: False,
    CONF_SPLIT_NWK: False,
    CONF_SPLIT_QUIRK: False,
}