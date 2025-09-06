"""API client for Bluestar Smart AC integration."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from .const import (
    BLUESTAR_BASE_URL,
    CONTROL_ENDPOINT,
    DEFAULT_BASE_URL,
    DEVICES_ENDPOINT,
    HEADERS,
    LOGIN_ENDPOINT,
    PREFERENCES_ENDPOINT,
    STATE_ENDPOINT,
    MQTT_SRC_KEY,
    MQTT_SRC_VALUE,
    MQTT_FORCE_SYNC_KEY,
)

_LOGGER = logging.getLogger(__name__)


class BluestarAPIError(Exception):
    """Exception raised for Bluestar API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class BluestarAPI:
    """API client for Bluestar Smart AC."""

    def __init__(
        self,
        phone: str,
        password: str,
        mqtt_gateway_url: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
    ):
        """Initialize the API client."""
        self.phone = phone
        self.password = password
        self.mqtt_gateway_url = mqtt_gateway_url
        self.base_url = base_url
        self.session_token: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    def _get_headers(self, session_token: Optional[str] = None) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = HEADERS.copy()
        if session_token:
            headers["X-APP-SESSION"] = session_token
        return headers

    async def login(self) -> Dict[str, Any]:
        """Login to Bluestar API."""
        if not self._session:
            raise BluestarAPIError("Session not initialized")

        login_payload = {
            "auth_id": self.phone,
            "auth_type": "phone",
            "password": self.password,
        }

        try:
            async with self._session.post(
                f"{self.base_url}{LOGIN_ENDPOINT}",
                headers=self._get_headers(),
                json=login_payload,
            ) as response:
                if response.status != 200:
                    raise BluestarAPIError(
                        f"Login failed: {response.status}", response.status
                    )

                data = await response.json()
                self.session_token = data.get("session_token")
                
                if not self.session_token:
                    raise BluestarAPIError("No session token received")
                
                _LOGGER.info("Login successful")
                return data

        except aiohttp.ClientError as err:
            raise BluestarAPIError(f"Login request failed: {err}")

    async def get_devices(self) -> Dict[str, Any]:
        """Get all devices."""
        if not self._session:
            raise BluestarAPIError("Session not initialized")

        if not self.session_token:
            await self.login()

        try:
            async with self._session.get(
                f"{self.base_url}{DEVICES_ENDPOINT}",
                headers=self._get_headers(self.session_token),
            ) as response:
                if response.status == 401:
                    # Session expired, try to re-login
                    await self.login()
                    async with self._session.get(
                        f"{self.base_url}{DEVICES_ENDPOINT}",
                        headers=self._get_headers(self.session_token),
                    ) as retry_response:
                        if retry_response.status != 200:
                            raise BluestarAPIError(
                                f"Failed to fetch devices: {retry_response.status}",
                                retry_response.status,
                            )
                        return await retry_response.json()

                if response.status != 200:
                    raise BluestarAPIError(
                        f"Failed to fetch devices: {response.status}", response.status
                    )

                return await response.json()

        except aiohttp.ClientError as err:
            raise BluestarAPIError(f"Devices request failed: {err}")

    async def control_device_gateway(
        self, device_id: str, control_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Control device via MQTT gateway (optional)."""
        if not self.mqtt_gateway_url:
            raise BluestarAPIError("MQTT gateway URL not configured")

        if not self._session:
            raise BluestarAPIError("Session not initialized")

        if not self.session_token:
            await self.login()

        try:
            async with self._session.post(
                f"{self.mqtt_gateway_url}/api/devices/{device_id}/control",
                headers={"Authorization": f"Bearer {self.session_token}"},
                json=control_data,
            ) as response:
                if response.status == 401:
                    # Session expired, try to re-login
                    await self.login()
                    async with self._session.post(
                        f"{self.mqtt_gateway_url}/api/devices/{device_id}/control",
                        headers={"Authorization": f"Bearer {self.session_token}"},
                        json=control_data,
                    ) as retry_response:
                        if retry_response.status != 200:
                            raise BluestarAPIError(
                                f"Gateway control failed: {retry_response.status}",
                                retry_response.status,
                            )
                        return await retry_response.json()

                if response.status != 200:
                    raise BluestarAPIError(
                        f"Gateway control failed: {response.status}", response.status
                    )

                return await response.json()

        except aiohttp.ClientError as err:
            raise BluestarAPIError(f"Gateway control request failed: {err}")

    async def control_device_direct(
        self, device_id: str, control_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Control device directly via Bluestar API (fallback)."""
        if not self._session:
            raise BluestarAPIError("Session not initialized")

        if not self.session_token:
            await self.login()

        # Add MQTT source and timestamp (exact match from working server.js)
        control_payload = control_data.copy()
        control_payload[MQTT_SRC_KEY] = MQTT_SRC_VALUE
        control_payload["ts"] = int(asyncio.get_event_loop().time() * 1000)

        headers = self._get_headers(self.session_token)

        try:
            # Step 1: Try preferences endpoint (exact mode control mechanism)
            if "mode" in control_payload:
                # Get current device state to determine mode
                devices_data = await self.get_devices()
                current_state = devices_data.get("states", {}).get(device_id, {})
                current_mode = current_state.get("state", {}).get("mode", 2)

                # Use new mode if being changed
                if isinstance(control_payload["mode"], dict):
                    current_mode = control_payload["mode"].get("value", current_mode)
                else:
                    current_mode = control_payload["mode"]

                # Build mode-specific preferences structure
                mode_config = {}
                for key, value in control_payload.items():
                    if key not in [MQTT_SRC_KEY, "ts"]:
                        if isinstance(value, dict):
                            mode_config[key] = str(value.get("value", value))
                        else:
                            mode_config[key] = str(value)

                preferences_payload = {
                    "preferences": {
                        "mode": {
                            str(current_mode): mode_config
                        }
                    }
                }

                async with self._session.post(
                    f"{self.base_url}{PREFERENCES_ENDPOINT.format(device_id=device_id)}",
                    headers=headers,
                    json=preferences_payload,
                ) as response:
                    if response.status == 200:
                        return await response.json()

            # Step 2: Fallback to direct MQTT structure
            mqtt_style_payload = {
                "state": {
                    "desired": control_payload
                }
            }

            async with self._session.post(
                f"{self.base_url}{STATE_ENDPOINT.format(device_id=device_id)}",
                headers=headers,
                json=mqtt_style_payload,
            ) as response:
                if response.status == 200:
                    return await response.json()

            # Step 3: Force sync if all methods fail
            force_sync_payload = {MQTT_FORCE_SYNC_KEY: 1}
            async with self._session.post(
                f"{self.base_url}{CONTROL_ENDPOINT.format(device_id=device_id)}",
                headers=headers,
                json=force_sync_payload,
            ) as response:
                if response.status == 200:
                    return await response.json()

            raise BluestarAPIError(f"All control methods failed: {response.status}")

        except aiohttp.ClientError as err:
            raise BluestarAPIError(f"Direct control request failed: {err}")

    async def control_device(self, device_id: str, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Control device using gateway first (if available), then direct API fallback."""
        # Try gateway first if configured
        if self.mqtt_gateway_url:
            try:
                return await self.control_device_gateway(device_id, control_data)
            except BluestarAPIError as err:
                _LOGGER.warning(f"Gateway control failed: {err}, trying direct API")

        # Always fallback to direct API (standalone mode)
        return await self.control_device_direct(device_id, control_data)

    async def force_sync(self, device_id: str) -> Dict[str, Any]:
        """Force sync device state."""
        control_data = {MQTT_FORCE_SYNC_KEY: 1}
        return await self.control_device(device_id, control_data)
