"""Climate platform for Bluestar Smart AC integration."""

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTemperature

from .const import (
    BLUESTAR_TO_FAN_MODE,
    BLUESTAR_TO_HVAC_MODE,
    FAN_MODE_TO_BLUESTAR,
    HVAC_MODE_TO_BLUESTAR,
    DOMAIN,
)
from .coordinator import BluestarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

_LOGGER.debug("CL1 climate module imported")

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bluestar climate entities."""
    _LOGGER.debug("CL2 climate async_setup_entry() start")
    
    try:
        # Check if coordinator exists in hass.data
        if config_entry.entry_id not in hass.data.get(DOMAIN, {}):
            _LOGGER.error("CLX coordinator not found in hass.data for entry_id=%s. Main integration setup may have failed.", config_entry.entry_id)
            _LOGGER.error("CLX available keys in hass.data[%s]: %s", DOMAIN, list(hass.data.get(DOMAIN, {}).keys()))
            return
        
        coordinator: BluestarDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
        _LOGGER.debug("CL3 got coordinator from hass.data")
        
        # Get all devices
        devices = coordinator.get_all_devices()
        _LOGGER.debug("CL4 found %d devices for climate platform", len(devices))
        
        entities = []
        for device_id in devices.keys():
            try:
                entity = BluestarClimateEntity(coordinator, device_id)
                entities.append(entity)
                _LOGGER.debug("CL5 created climate entity for device %s", device_id)
            except Exception as e:
                _LOGGER.exception("CL6 failed to create climate entity for device %s: %s", device_id, e)
        
        _LOGGER.debug("CL7 adding %d climate entities", len(entities))
        async_add_entities(entities, update_before_add=True)
        _LOGGER.debug("CL8 climate async_setup_entry() done")
        
    except Exception as e:
        _LOGGER.exception("CLX climate setup failed: %s", e)
        raise


class BluestarClimateEntity(CoordinatorEntity, ClimateEntity):
    """Representation of a Bluestar AC climate entity."""

    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.AUTO]
    _attr_fan_modes = ["low", "medium", "high", "auto"]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: BluestarDataUpdateCoordinator, device_id: str) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self.device_id = device_id
        self._attr_unique_id = f"{device_id}_climate"
        
        # Set device info
        device = coordinator.get_device(device_id)
        if device:
            self._attr_name = f"{device.get('name', 'Bluestar AC')} Climate"
        else:
            self._attr_name = f"Bluestar AC {device_id} Climate"

    @property
    def device_data(self) -> dict:
        """Get device data from coordinator."""
        return self.coordinator.get_device(self.device_id) or {}

    @property
    def device_name(self) -> str:
        """Get device name."""
        return self.device_data.get("name", f"Bluestar AC {self.device_id}")

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.device_data.get("current_temp")

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        return self.device_data.get("target_temp")

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        mode = self.device_data.get("mode")
        return BLUESTAR_TO_HVAC_MODE.get(mode, HVACMode.OFF)

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        fan_mode = self.device_data.get("fan_mode")
        return BLUESTAR_TO_FAN_MODE.get(fan_mode, "auto")

    @property
    def is_on(self) -> bool:
        """Return True if the AC is on."""
        return self.device_data.get("power", False)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature."""
        temperature = kwargs.get("temperature")
        if temperature is not None:
            await self.coordinator.set_temperature(self.device_id, temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode."""
        bluestar_mode = HVAC_MODE_TO_BLUESTAR.get(hvac_mode)
        if bluestar_mode:
            await self.coordinator.set_mode(self.device_id, bluestar_mode)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set the fan mode."""
        bluestar_fan_mode = FAN_MODE_TO_BLUESTAR.get(fan_mode)
        if bluestar_fan_mode:
            await self.coordinator.set_fan_mode(self.device_id, bluestar_fan_mode)

    async def async_turn_on(self) -> None:
        """Turn the AC on."""
        await self.coordinator.set_power(self.device_id, True)

    async def async_turn_off(self) -> None:
        """Turn the AC off."""
        await self.coordinator.set_power(self.device_id, False)