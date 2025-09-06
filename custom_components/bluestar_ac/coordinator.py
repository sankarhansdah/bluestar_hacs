"""Data update coordinator for Bluestar Smart AC integration."""

import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BluestarAPI, BluestarAPIError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BluestarDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Bluestar API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: BluestarAPI,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ):
        """Initialize the coordinator."""
        self.api = api
        self.devices: Dict[str, Any] = {}
        self.states: Dict[str, Any] = {}

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via library."""
        try:
            async with self.api as api:
                # Get devices and states
                data = await api.get_devices()
                
                # Extract devices and states
                self.devices = {device["thing_id"]: device for device in data.get("things", [])}
                self.states = data.get("states", {})
                
                # Process device data for easier access
                processed_devices = {}
                for device_id, device in self.devices.items():
                    state = self.states.get(device_id, {})
                    device_state = state.get("state", {})
                    
                    processed_devices[device_id] = {
                        "id": device_id,
                        "name": device.get("user_config", {}).get("name", "AC"),
                        "type": "ac",
                        "state": {
                            "power": device_state.get("pow", 0) == 1,
                            "mode": device_state.get("mode", 2),
                            "temperature": device_state.get("stemp", "24"),
                            "current_temp": device_state.get("ctemp", "27.5"),
                            "fan_speed": device_state.get("fspd", 2),
                            "vertical_swing": device_state.get("vswing", 0),
                            "horizontal_swing": device_state.get("hswing", 0),
                            "display": device_state.get("display", 0) != 0,
                            "connected": state.get("connected", False),
                            "rssi": device_state.get("rssi", -45),
                            "error": device_state.get("err", 0),
                            "source": device_state.get("src", "unknown"),
                            "timestamp": state.get("timestamp", 0),
                        },
                        "raw_device": device,
                        "raw_state": state,
                    }
                
                return {
                    "devices": processed_devices,
                    "raw_data": data,
                }

        except BluestarAPIError as err:
            raise UpdateFailed(f"Error communicating with Bluestar API: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")

    async def control_device(self, device_id: str, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Control a device."""
        try:
            async with self.api as api:
                result = await api.control_device(device_id, control_data)
                
                # Update local state immediately for better UX
                if device_id in self.data["devices"]:
                    device_data = self.data["devices"][device_id]
                    device_state = device_data["state"]
                    
                    # Update state with control data
                    for key, value in control_data.items():
                        if key == "pow":
                            device_state["power"] = value == 1
                        elif key == "mode":
                            device_state["mode"] = value
                        elif key == "stemp":
                            device_state["temperature"] = str(value)
                        elif key == "fspd":
                            device_state["fan_speed"] = value
                        elif key == "vswing":
                            device_state["vertical_swing"] = value
                        elif key == "hswing":
                            device_state["horizontal_swing"] = value
                        elif key == "display":
                            device_state["display"] = value != 0
                    
                    device_state["timestamp"] = int(asyncio.get_event_loop().time() * 1000)
                
                return result

        except BluestarAPIError as err:
            _LOGGER.error(f"Control failed for device {device_id}: {err}")
            raise

    async def force_sync_device(self, device_id: str) -> Dict[str, Any]:
        """Force sync a device."""
        try:
            async with self.api as api:
                return await api.force_sync(device_id)
        except BluestarAPIError as err:
            _LOGGER.error(f"Force sync failed for device {device_id}: {err}")
            raise

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device data by ID."""
        return self.data.get("devices", {}).get(device_id)

    def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device state by ID."""
        device = self.get_device(device_id)
        return device.get("state") if device else None

    def get_all_devices(self) -> Dict[str, Any]:
        """Get all devices."""
        return self.data.get("devices", {})
