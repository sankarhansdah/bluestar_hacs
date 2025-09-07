"""Climate platform for Bluestar Smart AC integration."""

import logging
from typing import Any, Dict, Optional

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BLUESTAR_TO_FAN_MODE,
    BLUESTAR_TO_HVAC_MODE,
    CONF_MQTT_GATEWAY_URL,
    DOMAIN,
    FAN_MODE_TO_BLUESTAR,
    HVAC_MODE_TO_BLUESTAR,
    MAX_TEMP,
    MIN_TEMP,
    TEMP_STEP,
)
from .coordinator import BluestarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Add module-level logging to see if file is imported
_LOGGER.info("🔍 Climate platform module loaded")


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bluestar Smart AC climate entities."""
    _LOGGER.info("🔍 async_setup_entry called for climate platform")
    
    coordinator: BluestarDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    devices = coordinator.get_all_devices()
    _LOGGER.info(f"🔍 Found {len(devices)} devices for climate setup")
    
    for device_id in devices.keys():
        _LOGGER.info(f"🔍 Creating climate entity for device: {device_id}")
        try:
            entity = BluestarClimateEntity(coordinator, device_id)
            entities.append(entity)
            _LOGGER.info(f"✅ Successfully created climate entity for {device_id}")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to create climate entity for {device_id}: {e}")

    _LOGGER.info(f"🔍 Created {len(entities)} climate entities")
    async_add_entities(entities)


class BluestarClimateEntity(CoordinatorEntity, ClimateEntity):
    """Representation of a Bluestar Smart AC climate entity."""

    _attr_hvac_modes = [HVACMode.OFF, HVACMode.FAN_ONLY, HVACMode.COOL, HVACMode.DRY, HVACMode.AUTO]
    _attr_fan_modes = ["low", "medium", "high", "auto"]
    _attr_temperature_unit = "celsius"
    _attr_target_temperature_step = TEMP_STEP
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.SWING_MODE
    )

    def __init__(self, coordinator: BluestarDataUpdateCoordinator, device_id: str) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self.device_id = device_id
        self._attr_unique_id = f"{device_id}_climate"
        
        # Set device info
        device = coordinator.get_device(device_id)
        if device:
            self._attr_name = f"{device['name']} Climate"
            self._attr_device_info = {
                "identifiers": {(DOMAIN, device_id)},
                "name": device["name"],
                "manufacturer": "Bluestar",
                "model": "Smart AC",
            }

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        state = self.coordinator.get_device_state(self.device_id)
        if state:
            try:
                return float(state.get("current_temp", 0))
            except (ValueError, TypeError):
                pass
        return None

    @property
    def target_temperature(self) -> Optional[float]:
        """Return the target temperature."""
        state = self.coordinator.get_device_state(self.device_id)
        if state:
            try:
                return float(state.get("temperature", 0))
            except (ValueError, TypeError):
                pass
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        state = self.coordinator.get_device_state(self.device_id)
        if not state or not state.get("power", False):
            return HVACMode.OFF
        
        mode = state.get("mode", 2)
        return HVACMode(BLUESTAR_TO_HVAC_MODE.get(mode, HVACMode.COOL))

    @property
    def fan_mode(self) -> Optional[str]:
        """Return current fan mode."""
        state = self.coordinator.get_device_state(self.device_id)
        if state:
            fan_speed = state.get("fan_speed", 2)
            return BLUESTAR_TO_FAN_MODE.get(fan_speed, "low")
        return "low"

    @property
    def swing_modes(self) -> Optional[list[str]]:
        """Return list of available swing modes."""
        return ["off", "vertical", "horizontal", "both"]

    @property
    def current_swing_mode(self) -> Optional[str]:
        """Return current swing mode."""
        state = self.coordinator.get_device_state(self.device_id)
        if not state:
            return "off"
        
        vswing = state.get("vertical_swing", 0) != 0
        hswing = state.get("horizontal_swing", 0) != 0
        
        if vswing and hswing:
            return "both"
        elif vswing:
            return "vertical"
        elif hswing:
            return "horizontal"
        else:
            return "off"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        state = self.coordinator.get_device_state(self.device_id)
        return state is not None and state.get("connected", False)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        control_data = HVAC_MODE_TO_BLUESTAR.get(hvac_mode, {})
        await self.coordinator.control_device(self.device_id, control_data)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature."""
        temperature = kwargs.get("temperature")
        if temperature is not None:
            control_data = {"stemp": f"{temperature:.1f}"}
            await self.coordinator.control_device(self.device_id, control_data)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan mode."""
        fan_speed = FAN_MODE_TO_BLUESTAR.get(fan_mode, 2)
        control_data = {"fspd": fan_speed}
        await self.coordinator.control_device(self.device_id, control_data)

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set swing mode."""
        control_data = {}
        
        if swing_mode in ["vertical", "both"]:
            control_data["vswing"] = 1
        else:
            control_data["vswing"] = 0
            
        if swing_mode in ["horizontal", "both"]:
            control_data["hswing"] = 1
        else:
            control_data["hswing"] = 0
        
        await self.coordinator.control_device(self.device_id, control_data)



