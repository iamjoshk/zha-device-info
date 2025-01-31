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