import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # Example: Fetch device info from zigpy
    from zigpy.zha.device import DeviceInfo

    # Replace with actual device fetching logic
    devices = [DeviceInfo(ieee="00:11:22:33:44:55:66:77", nwk=0x1234, manufacturer="Example", model="Model")]

    entities = [ZigbeeDeviceInfoSensor(device) for device in devices]
    async_add_entities(entities, True)

class ZigbeeDeviceInfoSensor(SensorEntity):
    def __init__(self, device_info):
        self._device_info = device_info
        self._name = f"Zigbee Device {device_info.ieee}"
        self._state = device_info.nwk

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            "ieee": self._device_info.ieee,
            "manufacturer": self._device_info.manufacturer,
            "model": self._device_info.model,
        }
