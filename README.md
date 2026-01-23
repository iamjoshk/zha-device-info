[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/iamjoshk/zha-device-info.svg)](https://github.com/iamjoshk/zha-device-info/releases)

# zha-device-info
ZHA zigbee device info as sensors in HA

## version 0.3.1
Added translation strings

### Past versions
v0.3.0 - made custom integration HACS compatible
v0.2.0 - Moved ZHA Device Info entities into their corresponding devices in the ZHA integration.
v0.1.0 - Initial creation and testing

## To add via HACS:
- copy the URL of this repo: https://github.com/iamjoshk/zha-device-info
- Go to your HACS dashboard and click the three dots menu in the top right
- select Custom repositories
- paste the URL into the Repository field and select Integration from the type dropdown
- click Add

Once the custom repo is added, then search for ZHA Device Info in the HACS dashboard and click. Then download it and restart Home Assistant.

Once HA restarts, go to Integrations and click Add Integration, then search for ZHA Device Info and add the integration.

### Configure
- When you add a new Entry, it will automatically find devices through your ZHA integration.
- By default, a new ZHA Device Info entity will be created in each ZHA device. This entity will have the device's Zigbee info as attributes.
    - Primary entity will use the IEEE as its state.
    - Attributes will be:
        - IEEE
        - NWK
        - Manufacturer
        - Model
        - Name
        - Quirk Applied
        - Quirk Class
        - Power Source
        - LQI
        - RSSI
        - Last Seen
        - Available
        - Device Type
- During set up (and later by clicking configure), you can choose to create separate entities for some of the attributes. The following entities can be created in the ZHA device:
    - Last Seen: as a `sensor` with  Last Seen as state
    - Availability: as a `binary_sensor` with Available as state
    - Power Source: as a `sensor` with Power Source as state
    - Network Adress: as a `sensor` with hex NWK address as state
    - Quirk Info: as a `binary_sensor` with Quirk Applied (as state) and Quirk Class (as attribute)
    - Device Type: as `sensor` Device Type as state

### Actions
The integration creates two new actions under Developer Tools -> Actions
- `zha_device_info.update` - updates your ZHA Device Info entities.
- `zha_device_info.export` - exports a json file with your ZHA Device Info entity data to /config/zha_devices.json (by default, but configurable)


### Using [flex-table-card](https://github.com/custom-cards/flex-table-card) to display ZHA Device Info
- install [flex-table-card](https://github.com/custom-cards/flex-table-card) from HACS
- On your dashboard, add flex-table-card and add the entities you want to display.
    - Example:
        ```
        type: custom:flex-table-card
        title: Zigbee Device Info
        clickable: true
        entities:
        include:
          - sensor.zha_device_info_entity*
        columns:
        - data: device
          name: Device Name
        - data: ieee
          name: IEEE
        - data: nwk
          name: NWK
        - data: device_type
          name: Type
        ```



---
Credit:
This integration used dmulcahey's https://github.com/dmulcahey/zha-device-exporter as the seed for the idea.
