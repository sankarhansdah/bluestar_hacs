"""Select platform for Bluestar Smart AC integration."""

import logging
from typing import Any, Dict, Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SWING_LABEL_TO_VALUE,
    SWING_OPTIONS,
    SWING_VALUE_TO_LABEL,
)
from .coordinator import BluestarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bluestar Smart AC select entities."""
    coordinator: BluestarDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    for device_id in coordinator.get_all_devices():
        entities.extend([
            BluestarVerticalSwingSelectEntity(coordinator, device_id),
            BluestarHorizontalSwingSelectEntity(coordinator, device_id),
        ])

    async_add_entities(entities)


class BluestarVerticalSwingSelectEntity(CoordinatorEntity, SelectEntity):
    """Representation of a Bluestar Smart AC vertical swing select entity."""

    _attr_options = [option["label"] for option in SWING_OPTIONS]

    def __init__(self, coordinator: BluestarDataUpdateCoordinator, device_id: str) -> None:
        """Initialize the vertical swing select entity."""
        super().__init__(coordinator)
        self.device_id = device_id
        self._attr_unique_id = f"{device_id}_vertical_swing"
        
        # Set device info
        device = coordinator.get_device(device_id)
        if device:
            self._attr_name = f"{device['name']} Vertical Swing"
            self._attr_device_info = {
                "identifiers": {(DOMAIN, device_id)},
                "name": device["name"],
                "manufacturer": "Bluestar",
                "model": "Smart AC",
            }

    @property
    def current_option(self) -> Optional[str]:
        """Return the current selected option."""
        state = self.coordinator.get_device_state(self.device_id)
        if state:
            vswing = state.get("vertical_swing", 0)
            return SWING_VALUE_TO_LABEL.get(vswing, "Off")
        return "Off"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        state = self.coordinator.get_device_state(self.device_id)
        return state is not None and state.get("connected", False)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        value = SWING_LABEL_TO_VALUE.get(option, 0)
        control_data = {"vswing": value}
        await self.coordinator.control_device(self.device_id, control_data)


class BluestarHorizontalSwingSelectEntity(CoordinatorEntity, SelectEntity):
    """Representation of a Bluestar Smart AC horizontal swing select entity."""

    _attr_options = [option["label"] for option in SWING_OPTIONS]

    def __init__(self, coordinator: BluestarDataUpdateCoordinator, device_id: str) -> None:
        """Initialize the horizontal swing select entity."""
        super().__init__(coordinator)
        self.device_id = device_id
        self._attr_unique_id = f"{device_id}_horizontal_swing"
        
        # Set device info
        device = coordinator.get_device(device_id)
        if device:
            self._attr_name = f"{device['name']} Horizontal Swing"
            self._attr_device_info = {
                "identifiers": {(DOMAIN, device_id)},
                "name": device["name"],
                "manufacturer": "Bluestar",
                "model": "Smart AC",
            }

    @property
    def current_option(self) -> Optional[str]:
        """Return the current selected option."""
        state = self.coordinator.get_device_state(self.device_id)
        if state:
            hswing = state.get("horizontal_swing", 0)
            return SWING_VALUE_TO_LABEL.get(hswing, "Off")
        return "Off"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        state = self.coordinator.get_device_state(self.device_id)
        return state is not None and state.get("connected", False)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        value = SWING_LABEL_TO_VALUE.get(option, 0)
        control_data = {"hswing": value}
        await self.coordinator.control_device(self.device_id, control_data)
