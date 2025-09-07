"""The Bluestar Smart AC integration."""
from __future__ import annotations

import asyncio
import logging
import traceback
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .api import BluestarAPI
from .const import (
    CONF_BASE_URL,
    CONF_PASSWORD,
    CONF_PHONE,
    DOMAIN,
)
from .coordinator import BluestarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.SENSOR,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Bluestar Smart AC component."""
    _LOGGER.debug("B1 async_setup() called")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluestar Smart AC from a config entry."""
    _LOGGER.debug("B2 async_setup_entry() start for entry_id=%s title=%s", entry.entry_id, entry.title)
    hass.data.setdefault(DOMAIN, {})

    try:
        _LOGGER.debug("B3 creating API client")
        # Create API client
        api = BluestarAPI(
            phone=entry.data[CONF_PHONE],
            password=entry.data[CONF_PASSWORD],
            base_url=entry.data.get(CONF_BASE_URL),
        )

        _LOGGER.debug("B4 logging in to API")
        # Login to API
        await api.login()

        _LOGGER.debug("B5 creating coordinator")
        # Create coordinator
        coordinator = BluestarDataUpdateCoordinator(hass, api)
        
        _LOGGER.debug("B6 first refresh start")
        # Fetch initial data
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.debug("B7 first refresh OK")

        hass.data[DOMAIN][entry.entry_id] = coordinator
        _LOGGER.debug("B8 stored hass.data for entry")

        _LOGGER.debug("B9 forward_entry_setups -> %s", PLATFORMS)
        # Set up platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.debug("B10 all platforms forwarded")

        _LOGGER.debug("B11 async_setup_entry() done")
        return True

    except asyncio.TimeoutError as e:
        _LOGGER.exception("TMO: Timeout during setup at breadcrumb above. %s", e)
        raise ConfigEntryNotReady from e
    except Exception as e:
        _LOGGER.error(
            "FATAL in async_setup_entry at breadcrumb above: %s\n%s",
            e, traceback.format_exc()
        )
        # Use NotReady if the problem is likely transient (network). Otherwise re-raise to mark failed setup.
        raise


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)



