"""Tests for Bluestar Smart AC integration."""

import pytest
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.bluestar_ac import async_setup_entry
from custom_components.bluestar_ac.const import DOMAIN


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    return ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="Test Bluestar AC",
        data={
            "phone": "+919876543210",
            "password": "test_password",
            "mqtt_gateway_url": "http://localhost:3000",
            "base_url": "https://api.bluestarindia.com/prod",
        },
        source="user",
        options={},
        entry_id="test_entry_id",
    )


@pytest.mark.asyncio
async def test_async_setup_entry(hass: HomeAssistant, mock_config_entry):
    """Test async_setup_entry."""
    with patch("custom_components.bluestar_ac.BluestarAPI") as mock_api, \
         patch("custom_components.bluestar_ac.BluestarDataUpdateCoordinator") as mock_coordinator:
        
        # Mock coordinator methods
        mock_coordinator_instance = AsyncMock()
        mock_coordinator_instance.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator.return_value = mock_coordinator_instance
        
        # Mock API
        mock_api_instance = AsyncMock()
        mock_api.return_value = mock_api_instance
        
        result = await async_setup_entry(hass, mock_config_entry)
        
        assert result is True
        assert DOMAIN in hass.data
        assert mock_config_entry.entry_id in hass.data[DOMAIN]



