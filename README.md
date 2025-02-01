# zha-device-info
ZHA zigbee device info as sensors in HA

## version 0.0.1
Initial creation and testing

## To add as a custom integration:
- download the zip
- in your config directory, under custom_components, extract zip to zha_device_info folder.
- Add the integration through the Integration config flow UI.
- Click Add Entry for the integration to find all of the devices in your ZHA integration and add them to the ZHA Device Info integration.

### Actions
`zha_device_info.update` - updates your ZHA Device Info entities
`zha_device_info.export` - exports a json file with your ZHA Device Info entity data to /config/zha_devices.json (by default, but configurable)


---
Uses dmulcahey's https://github.com/dmulcahey/zha-device-exporter as launch pad.