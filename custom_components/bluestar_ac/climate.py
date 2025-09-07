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
from homeassistant.const import UnitOfTemperature

from .const import (
    BLUESTAR_TO_FAN_MODE,
    BLUESTAR_TO_HVAC_MODE,
    FAN_MODE_TO_BLUESTAR,
    HVAC_MODE_TO_BLUESTAR,
)
from .coordinator import BluestarDataUpdateCoordinator
from .entity import BluestarEntity

_LOGGER = logging.getLogger(__name__)

_LOGGER.info("🔍 Climate platform module loaded")

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bluestar climate entities."""
    _LOGGER.info("🔍 async_setup_entry called for climate platform")
    
    coordinator: BluestarDataUpdateCoordinator = hass.data[config_entry.entry_id]
    
    # Get all devices
    devices = coordinator.get_all_devices()
    _LOGGER.info(f"🔍 Found {len(devices)} devices for climate platform")
    
    entities = []
    for device_id in devices.keys():
        try:
            entity = BluestarClimateEntity(coordinator, device_id)
            entities.append(entity)
            _LOGGER.info(f"✅ Created climate entity for device {device_id}")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to create climate entity for device {device_id}: {e}")
    
    _LOGGER.info(f"🔍 Adding {len(entities)} climate entities")
    async_add_entities(entities)


class BluestarClimateEntity(BluestarEntity, ClimateEntity):
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
        super().__init__(coordinator, device_id)
        self._attr_name = f"{self.device_name} Climate"

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