"""Test climate platform for Bluestar Smart AC integration."""

import logging

_LOGGER = logging.getLogger(__name__)

# Test if this file can be imported
_LOGGER.info("🔍 TEST: Climate test module loaded")

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Test setup function."""
    _LOGGER.info("🔍 TEST: async_setup_entry called")
    return True
