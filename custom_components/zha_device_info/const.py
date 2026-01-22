"""Constants for ZHA Device Info integration."""

import voluptuous as vol

DOMAIN = "zha_device_info"
PLATFORMS = ["sensor", "binary_sensor"]

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
CONF_SPLIT_LAST_SEEN = "split_last_seen"  # Changed format
CONF_SPLIT_AVAILABILITY = "split_availability"  # Changed format
CONF_SPLIT_POWER = "split_power_source"  # Changed format
CONF_SPLIT_NWK = "split_network_address"  # Changed format
CONF_SPLIT_QUIRK = "split_quirk_info"  # Changed format
CONF_SPLIT_DEVICE_TYPE = "split_device_type"  # Changed format

SPLITTABLE_ATTRIBUTES = {
    CONF_SPLIT_LAST_SEEN: {
        "name": "Last Seen",
        "attributes": [ATTR_LAST_SEEN],
        "icon": "mdi:clock-outline",
        "device_class": "timestamp",
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
    CONF_SPLIT_DEVICE_TYPE: {
        "name": "Device Type",
        "attributes": [ATTR_DEVICE_TYPE],
        "icon": "mdi:tag",
        "device_class": None,
    },
    # Keep these in SPLITTABLE_ATTRIBUTES for config flow
    CONF_SPLIT_AVAILABILITY: {
        "name": "Availability",
        "attributes": [ATTR_AVAILABLE],
        "icon": "mdi:check-network-outline",
        "device_class": None,
        "platform": "binary_sensor",  # Add platform identifier
    },
    CONF_SPLIT_QUIRK: {
        "name": "Quirk Info",
        "attributes": [ATTR_QUIRK_APPLIED, ATTR_QUIRK_CLASS],
        "icon": "mdi:puzzle",
        "device_class": None,
        "platform": "binary_sensor",  # Add platform identifier
    },
}

# Display names for configuration options
CONF_NAMES = {
    "split_last_seen": "Split Last Seen",
    "split_availability": "Split Availability",
    "split_power_source": "Split Power Source",
    "split_network_address": "Split Network Address",
    "split_quirk_info": "Split Quirk Info",
    "split_device_type": "Split Device Type",
}

# Default configuration
DEFAULT_OPTIONS = {
    CONF_SPLIT_LAST_SEEN: False,
    CONF_SPLIT_AVAILABILITY: False,
    CONF_SPLIT_POWER: False,
    CONF_SPLIT_NWK: False,
    CONF_SPLIT_QUIRK: False,
    CONF_SPLIT_DEVICE_TYPE: False,
}