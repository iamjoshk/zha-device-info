# zha-device-info
ZHA zigbee device info as sensors in HA

## version 0.2.0
Moved ZHA Device Info entities into their corresponding devices in the ZHA integration.

### version 0.1.0
Initial creation and testing

## To add as a custom integration:
- download the zip
- in your config directory, under custom_components, extract zip to zha_device_info folder, then restart HA.
- after restart, under Integrations, click Add Integration, then search and select ZHA Device Info from list.
- Click Add Entry for the integration to find all of the devices in your ZHA integration and add them to the ZHA Device Info integration.

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


> For my own convenience, I forked flex-table-card to add a search box to the top of the card that lets me filter the table to show me rows that I want to see (like when I want to search for a NWK ID because of an error message in the log). My fork: https://github.com/iamjoshk/flex-table-card

---
Credit:
This integration used dmulcahey's https://github.com/dmulcahey/zha-device-exporter as the seed for the idea.
