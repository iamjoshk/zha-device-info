"""Test fixtures for ZHA Device Info integration tests."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.components.zha.core.const import DOMAIN as ZHA_DOMAIN

@pytest.fixture
def mock_zha_device():
    """Mock ZHA device for testing."""
    device = Mock()
    device.name = "Test Device"
    device.ieee = "00:11:22:33:44:55:66:77"
    device.nwk = 0x1234
    device.manufacturer = "Test Manufacturer"
    device.model = "Test Model"
    device.quirk_applied = True
    device.quirk_class = "TestQuirk"
    device.power_source = "Battery"
    device.lqi = 255
    device.rssi = -60
    device.last_seen = datetime.now().timestamp()
    device.available = True
    return device

@pytest.fixture
def mock_gateway():
    """Mock ZHA gateway for testing."""
    gateway = Mock()
    gateway.devices = {}
    return gateway

@pytest.fixture
def mock_zha_data(mock_gateway):
    """Mock ZHA data for testing."""
    zha_data = Mock()
    zha_data.gateway_proxy = Mock()
    zha_data.gateway_proxy.gateway = mock_gateway
    return zha_data

@pytest.fixture
def hass(mock_zha_data):
    """Mock Home Assistant instance for testing."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {
        ZHA_DOMAIN: mock_zha_data,
        "zha_device_info": {
            "device_registry": {},
            "entities": []
        }
    }
    return hass
