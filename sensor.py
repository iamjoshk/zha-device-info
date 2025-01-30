import logging
import sqlite3
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity
from zha.zigbee.device import DeviceInfo

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    db_path = hass.config.path("zigbee.db")
    devices = []

    try:
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        cursor = conn.cursor()
        
        # Example query joining multiple tables to gather all necessary device information
        cursor.execute("""
            SELECT d.ieee, d.nwk, d.manufacturer, d.model, d.name, d.quirk_applied, d.quirk_class, d.quirk_id, 
                   d.manufacturer_code, d.power_source, d.lqi, d.rssi, d.last_seen, d.available, d.device_type, d.signature,
                   e.endpoint_id, e.profile_id, e.device_type, c.cluster_id, c.cluster_type
            FROM devices_v13 d
            LEFT JOIN endpoints_v13 e ON d.ieee = e.ieee
            LEFT JOIN clusters_v13 c ON e.endpoint_id = c.endpoint_id
        """)
        rows = cursor.fetchall()

        for row in rows:
            devices.append(DeviceInfo(
                ieee=row[0],
                nwk=row[1],
                manufacturer=row[2],
                model=row[3],
                name=row[4],
                quirk_applied=row[5],
                quirk_class=row[6],
                quirk_id=row[7],
                manufacturer_code=row[8],
                power_source=row[9],
                lqi=row[10],
                rssi=row[11],
                last_seen=row[12],
                available=row[13],
                device_type=row[14],
                signature=row[15]
            ))

        conn.close()
    except sqlite3.Error as e:
        _LOGGER.error(f"Error reading zigbee.db: {e}")
    except sqlite3.OperationalError as e:
        _LOGGER.error(f"Operational error reading zigbee.db: {e}")

    if devices:
        entities = [ZigbeeDeviceInfoSensor(device) for device in devices]
        async_add_entities(entities, True)
    else:
        _LOGGER.warning("No devices found in zigbee.db")

class ZigbeeDeviceInfoSensor(Entity):
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
            "name": self._device_info.name,
            "quirk_applied": self._device_info.quirk_applied,
            "quirk_class": self._device_info.quirk_class,
            "quirk_id": self._device_info.quirk_id,
            "manufacturer_code": self._device_info.manufacturer_code,
            "power_source": self._device_info.power_source,
            "lqi": self._device_info.lqi,
            "rssi": self._device_info.rssi,
            "last_seen": self._device_info.last_seen,
            "available": self._device_info.available,
            "device_type": self._device_info.device_type,
            "signature": self._device_info.signature,
        }