# zha-device-info
ZHA zigbee device info as sensors in HA

## version 0.1.0
Initial creation and testing

## To add as a custom integration:
- download the zip
- in your config directory, under custom_components, extract zip to zha_device_info folder, then restart HA.
- after restart, under Integrations, click Add Integration, then search and select ZHA Device Info from list.
- Click Add Entry for the integration to find all of the devices in your ZHA integration and add them to the ZHA Device Info integration.

### Configure
- When you add a new Entry, it will automatically find devices through your ZHA integration.
- By default, each ZHA device will create a ZHA Device Info device with a single, primary entity. This entity will have the device's ZHA info as attributes.
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
- During set up (and later by clicking configure), you can choose to create separate entities for some of the attributes. The following entities can be created:
    - Last Seen: as a `sensor` with  Last Seen as state
    - Availability: as a `binary_sensor` with Available as state
    - Power Source: as a `sensor` with Power Source as state
    - Network Adress: as a `sensor` with hex NWK address as state
    - Quirk Info: as a `binary_sensor` with Quirk Applied (as state) and Quirk Class (as attribute)
    - Device Type: as `sensor` Device Type as state

### Actions
The integration creates two new actions under Developer Tools -> Actions
`zha_device_info.update` - updates your ZHA Device Info entities.
`zha_device_info.export` - exports a json file with your ZHA Device Info entity data to /config/zha_devices.json (by default, but configurable)


---
Credit:
This integration used dmulcahey's https://github.com/dmulcahey/zha-device-exporter as the seed for the idea.
