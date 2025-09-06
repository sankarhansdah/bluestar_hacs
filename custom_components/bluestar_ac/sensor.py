"""Sensor platform for Bluestar Smart AC integration."""

import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
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
    """Set up Bluestar Smart AC sensor entities."""
    coordinator: BluestarDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    for device_id in coordinator.get_all_devices():
        entities.extend([
            BluestarRSSISensorEntity(coordinator, device_id),
            BluestarErrorSensorEntity(coordinator, device_id),
        ])

    async_add_entities(entities)


class BluestarRSSISensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of a Bluestar Smart AC RSSI sensor entity."""

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = "dBm"

    def __init__(self, coordinator: BluestarDataUpdateCoordinator, device_id: str) -> None:
        """Initialize the RSSI sensor entity."""
        super().__init__(coordinator)
        self.device_id = device_id
        self._attr_unique_id = f"{device_id}_rssi"
        
        # Set device info
        device = coordinator.get_device(device_id)
        if device:
            self._attr_name = f"{device['name']} RSSI"
            self._attr_device_info = {
                "identifiers": {(DOMAIN, device_id)},
                "name": device["name"],
                "manufacturer": "Bluestar",
                "model": "Smart AC",
            }

    @property
    def native_value(self) -> Optional[int]:
        """Return the RSSI value."""
        state = self.coordinator.get_device_state(self.device_id)
        if state:
            return state.get("rssi", -45)
        return -45

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        state = self.coordinator.get_device_state(self.device_id)
        return state is not None and state.get("connected", False)


class BluestarErrorSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of a Bluestar Smart AC error sensor entity."""

    def __init__(self, coordinator: BluestarDataUpdateCoordinator, device_id: str) -> None:
        """Initialize the error sensor entity."""
        super().__init__(coordinator)
        self.device_id = device_id
        self._attr_unique_id = f"{device_id}_error"
        
        # Set device info
        device = coordinator.get_device(device_id)
        if device:
            self._attr_name = f"{device['name']} Error Code"
            self._attr_device_info = {
                "identifiers": {(DOMAIN, device_id)},
                "name": device["name"],
                "manufacturer": "Bluestar",
                "model": "Smart AC",
            }

    @property
    def native_value(self) -> Optional[int]:
        """Return the error code."""
        state = self.coordinator.get_device_state(self.device_id)
        if state:
            return state.get("error", 0)
        return 0

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        state = self.coordinator.get_device_state(self.device_id)
        return state is not None and state.get("connected", False)
