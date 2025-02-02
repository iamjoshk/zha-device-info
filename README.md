# zha-device-info
ZHA zigbee device info as sensors in HA

## version 0.0.1
Initial creation and testing

## To add as a custom integration:
- download the zip
- in your config directory, under custom_components, extract zip to zha_device_info folder.
- Add the integration through the Integration config flow UI.
- Click Add Entry for the integration to find all of the devices in your ZHA integration and add them to the ZHA Device Info integration.

### Configure
- When you a new Entry, it will automatically find devices through your ZHA integration.
- By default, each ZHA device will create a ZHA Device Info device with a single entity. This entity will have the devices ZHA info as attributes.
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
- During set up (and later by clicking configure), you can choose to create separate entities for some of the attributes. These attributes are:
    - Signal Strength: LQI (as state) and RSSI (as attribute)
    - Last Seen: Last Seen as state
    - Availability: Available as state
    - Power Source: Power Source as state
    - Network Adress: NWK address as hex
    - Quirk Info: Quirk Applied (as state) and Quirk Class (as attribute)
    - Device Type: Device Type as state

### Actions
`zha_device_info.update` - updates your ZHA Device Info entities
`zha_device_info.export` - exports a json file with your ZHA Device Info entity data to /config/zha_devices.json (by default, but configurable)


---
Uses dmulcahey's https://github.com/dmulcahey/zha-device-exporter as launch pad for idea.