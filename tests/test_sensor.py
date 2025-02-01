"""Tests for ZHA Device Info sensor."""
from unittest.mock import Mock, patch
import pytest

from custom_components.zha_device_info.sensor import ZHADeviceInfoSensor

async def test_sensor_attributes(hass, mock_zha_device):
    """Test sensor attributes are set correctly."""
    device_registry = Mock()
    device_registry.async_get_device.return_value = None
    
    sensor = ZHADeviceInfoSensor(hass, mock_zha_device, device_registry)
    
    attributes = sensor.extra_state_attributes
    assert attributes["ieee"] == "00:11:22:33:44:55:66:77"
    assert attributes["nwk"] == "0x1234"
    assert attributes["manufacturer"] == "Test Manufacturer"
    assert attributes["model"] == "Test Model"
    assert attributes["quirk_applied"] is True
    assert attributes["quirk_class"] == "TestQuirk"

async def test_sensor_name_by_user(hass, mock_zha_device):
    """Test sensor uses name_by_user when available."""
    device_registry = Mock()
    mock_entry = Mock()
    mock_entry.name_by_user = "Custom Name"
    device_registry.async_get_device.return_value = mock_entry
    
    sensor = ZHADeviceInfoSensor(hass, mock_zha_device, device_registry)
    assert sensor.name == "ZHA Device Info Custom Name"
