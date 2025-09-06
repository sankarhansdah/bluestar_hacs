"""Switch platform for Bluestar Smart AC integration."""

import logging
from typing import Any, Dict, Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BluestarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bluestar Smart AC switch entities."""
    coordinator: BluestarDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    for device_id in coordinator.get_all_devices():
        entities.append(BluestarDisplaySwitchEntity(coordinator, device_id))

    async_add_entities(entities)


class BluestarDisplaySwitchEntity(CoordinatorEntity, SwitchEntity):
    """Representation of a Bluestar Smart AC display switch entity."""

    def __init__(self, coordinator: BluestarDataUpdateCoordinator, device_id: str) -> None:
        """Initialize the display switch entity."""
        super().__init__(coordinator)
        self.device_id = device_id
        self._attr_unique_id = f"{device_id}_display"
        
        # Set device info
        device = coordinator.get_device(device_id)
        if device:
            self._attr_name = f"{device['name']} Display"
            self._attr_device_info = {
                "identifiers": {(DOMAIN, device_id)},
                "name": device["name"],
                "manufacturer": "Bluestar",
                "model": "Smart AC",
            }

    @property
    def is_on(self) -> Optional[bool]:
        """Return if the switch is on."""
        state = self.coordinator.get_device_state(self.device_id)
        if state:
            return state.get("display", False)
        return False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        state = self.coordinator.get_device_state(self.device_id)
        return state is not None and state.get("connected", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        control_data = {"display": 1}
        await self.coordinator.control_device(self.device_id, control_data)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        control_data = {"display": 0}
        await self.coordinator.control_device(self.device_id, control_data)
