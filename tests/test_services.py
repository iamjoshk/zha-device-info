"""Tests for ZHA Device Info services."""
from unittest.mock import Mock, patch
import pytest
from custom_components.zha_device_info.services import async_register_services

async def test_update_service(hass, mock_zha_device, mock_gateway):
    """Test the update service."""
    mock_gateway.devices = {"test_ieee": mock_zha_device}
    
    await async_register_services(hass)
    await hass.services.async_call(
        "zha_device_info",
        "update",
        blocking=True
    )
    
    device_registry = hass.data["zha_device_info"]["device_registry"]
    assert len(device_registry) == 1
    device_info = device_registry["00:11:22:33:44:55:66:77"]
    assert device_info["manufacturer"] == "Test Manufacturer"
    assert device_info["model"] == "Test Model"
    assert device_info["quirk_class"] == "TestQuirk"

async def test_export_service(hass, mock_zha_device, tmp_path):
    """Test the export service."""
    export_path = tmp_path / "export.json"
    
    hass.data["zha_device_info"]["device_registry"] = {
        "test_ieee": {"name": "Test Device"}
    }
    
    await async_register_services(hass)
    await hass.services.async_call(
        "zha_device_info",
        "export",
        {"path": str(export_path)},
        blocking=True
    )
    
    assert export_path.exists()
