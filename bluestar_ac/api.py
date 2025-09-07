"""Bluestar Smart AC API client with MQTT support."""
import asyncio
import base64
import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp

# Try to import MQTT, but make it optional
try:
    import paho.mqtt.client as mqtt_client
    import ssl
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    _LOGGER = logging.getLogger(__name__)
    _LOGGER.warning("paho-mqtt not available, MQTT functionality disabled")

from .const import (
    DEFAULT_BASE_URL,
    LOGIN_ENDPOINT,
    DEVICES_ENDPOINT,
    CONTROL_ENDPOINT,
    PREFERENCES_ENDPOINT,
    STATE_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)


class BluestarAPIError(Exception):
    """Exception raised for Bluestar API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class BluestarAPIAuthError(Exception):
    """Exception raised for authentication errors."""

    def __init__(self, message: str):
        super().__init__(message)


class BluestarAPITemporaryError(Exception):
    """Exception raised for temporary server errors."""

    def __init__(self, message: str):
        super().__init__(message)


class BluestarCredentialExtractor:
    """Extract and manage MQTT credentials from login response."""
    
    def __init__(self):
        self.credentials = None
    
    def extract_credentials(self, login_response: Dict[str, Any]) -> Dict[str, str]:
        """Extract MQTT credentials from login response."""
        try:
            mi = login_response.get("mi")
            if not mi:
                raise BluestarAPIError("No 'mi' field in login response")
            
            # Decode Base64 and split by "::"
            decoded = base64.b64decode(mi).decode('utf-8')
            parts = decoded.split('::')
            
            if len(parts) != 3:
                raise BluestarAPIError(f"Invalid credential format. Expected 3 parts, got {len(parts)}")
            
            endpoint, access_key, secret_key = parts
            
            self.credentials = {
                "endpoint": endpoint,
                "access_key": access_key,
                "secret_key": secret_key,
                "session_id": login_response.get("session"),
                "user_id": login_response.get("user", {}).get("id"),
                "raw": mi
            }
            
            _LOGGER.info("✅ Credentials extracted successfully")
            _LOGGER.info(f"📍 Endpoint: {endpoint}")
            _LOGGER.info(f"🔑 Access Key: {access_key[:8]}...")
            _LOGGER.info(f"🔐 Secret Key: {secret_key[:8]}...")
            _LOGGER.info(f"🆔 Session ID: {login_response.get('session')}")
            
            return self.credentials
            
        except Exception as error:
            _LOGGER.error(f"❌ Failed to extract credentials: {error}")
            raise BluestarAPIError(f"Failed to extract credentials: {error}")
    
    def get_credentials(self) -> Optional[Dict[str, str]]:
        """Get current credentials."""
        return self.credentials
    
    def is_valid(self) -> bool:
        """Check if credentials are valid."""
        return (self.credentials and 
                self.credentials.get("endpoint") and 
                self.credentials.get("access_key") and 
                self.credentials.get("secret_key") and 
                self.credentials.get("session_id"))


class BluestarMQTTClient:
    """MQTT client for Bluestar Smart AC control."""
    
    def __init__(self, credentials: Dict[str, str]):
        if not MQTT_AVAILABLE:
            raise ImportError("MQTT functionality not available - paho-mqtt not installed")
            
        self.credentials = credentials
        self.client = None
        self.is_connected = False
        self.client_id = f"u-{credentials['session_id']}"
        
        # EXACT CONSTANTS FROM DECOMPILED APP
        self.FORCE_FETCH_KEY_NAME = "fpsh"
        self.PUB_CONTROL_TOPIC_NAME = "things/%s/control"
        self.PUB_STATE_UPDATE_TOPIC_NAME = "$aws/things/%s/shadow/update"
        self.SRC_KEY = "src"
        self.SRC_VALUE = "anmq"
        
        _LOGGER.info("🔧 Bluestar MQTT Client created")
    
    async def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            self.client = mqtt_client.Client(self.client_id)
            
            # Configure SSL/TLS
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            self.client.tls_set_context(context)
            
            # Set up event handlers
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_error = self._on_error
            
            # Connect to broker
            endpoint = self.credentials["endpoint"]
            _LOGGER.info(f"🔌 Connecting to MQTT broker: {endpoint}")
            
            self.client.connect(endpoint, 443, 30)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 30
            while not self.is_connected and timeout > 0:
                await asyncio.sleep(1)
                timeout -= 1
            
            if self.is_connected:
                _LOGGER.info("✅ MQTT Connected successfully")
                return True
            else:
                _LOGGER.error("❌ MQTT connection timeout")
                return False
                
        except Exception as error:
            _LOGGER.error(f"❌ Failed to connect to MQTT: {error}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection."""
        if rc == 0:
            self.is_connected = True
            _LOGGER.info("🔗 MQTT Connected successfully")
        else:
            _LOGGER.error(f"❌ MQTT Connection failed with code {rc}")
            self.is_connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection."""
        self.is_connected = False
        _LOGGER.info("📴 MQTT Disconnected")
    
    def _on_error(self, client, userdata, error):
        """Handle MQTT errors."""
        _LOGGER.error(f"❌ MQTT Error: {error}")
        self.is_connected = False
    
    def publish(self, device_id: str, control_payload: Dict[str, Any]) -> bool:
        """Publish control command via MQTT."""
        if not self.is_connected:
            _LOGGER.error("❌ MQTT not connected")
            return False
        
        try:
            # Step 1: Add src key (EXACT from decompiled app)
            control_payload[self.SRC_KEY] = self.SRC_VALUE
            
            # Step 2: Create desired object
            desired_object = control_payload.copy()
            
            # Step 3: Create state object
            state_object = {
                "state": {
                    "desired": desired_object
                }
            }
            
            # Step 4: Format topic
            topic = self.PUB_STATE_UPDATE_TOPIC_NAME % device_id
            
            _LOGGER.info(f"📤 MQTT Publish: {json.dumps(state_object, indent=2)}")
            _LOGGER.info(f"📤 Topic: {topic}")
            
            # Step 5: Publish with QOS0
            result = self.client.publish(topic, json.dumps(state_object), qos=0)
            
            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                _LOGGER.info("✅ Successfully published via MQTT")
                return True
            else:
                _LOGGER.error(f"❌ Failed to publish via MQTT: {result.rc}")
                return False
                
        except Exception as error:
            _LOGGER.error(f"❌ MQTT Publish Error: {error}")
            return False
    
    def force_sync(self, device_id: str) -> bool:
        """Send force sync command via MQTT."""
        if not self.is_connected:
            _LOGGER.error("❌ MQTT not connected")
            return False
        
        try:
            # Create force sync payload
            force_sync_payload = {self.FORCE_FETCH_KEY_NAME: 1}
            
            # Format topic
            topic = self.PUB_CONTROL_TOPIC_NAME % device_id
            
            _LOGGER.info(f"📤 MQTT Force Sync: {json.dumps(force_sync_payload, indent=2)}")
            _LOGGER.info(f"📤 Topic: {topic}")
            
            # Publish with QOS0
            result = self.client.publish(topic, json.dumps(force_sync_payload), qos=0)
            
            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                _LOGGER.info("✅ Successfully published force sync via MQTT")
                return True
            else:
                _LOGGER.error(f"❌ Failed to publish force sync via MQTT: {result.rc}")
                return False
                
        except Exception as error:
            _LOGGER.error(f"❌ MQTT Force Sync Error: {error}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            _LOGGER.info("🔌 MQTT Disconnected")


class BluestarAPI:
    """Bluestar Smart AC API client with MQTT support."""

    def __init__(
        self,
        phone: str,
        password: str,
        base_url: str = DEFAULT_BASE_URL,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self.phone = phone
        self.password = password
        self.base_url = base_url
        self._session = session
        self.session_token: Optional[str] = None
        self.credential_extractor = BluestarCredentialExtractor()
        self.mqtt_client: Optional[BluestarMQTTClient] = None

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        if self._session:
            await self._session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def _get_auth_headers(self, session_token: Optional[str] = None) -> Dict[str, str]:
        """Get authentication headers (EXACTLY matching the Android app)."""
        token = session_token or self.session_token
        return {
            "X-APP-VER": "v4.11.4-133",
            "X-OS-NAME": "Android",
            "X-OS-VER": "v13-33",
            "User-Agent": "com.bluestarindia.bluesmart",
            "Content-Type": "application/json",
            "X-APP-SESSION": token or "",
        }

    async def login(self) -> Dict[str, Any]:
        """Login to Bluestar API with retry logic and multiple phone formats."""
        _LOGGER.info(f"🔐 Attempting login for phone: {self.phone}")
        
        # Try multiple base URLs (AWS and classic)
        base_candidates = []
        if self.base_url:
            base_candidates.append(self.base_url.rstrip("/"))
        
        # Add fallback to the other known host
        other_base = "https://api.bluestarindia.com/prod" \
            if "execute-api" in (self.base_url or "") else \
            "https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod"
        base_candidates.append(other_base)
        
        # Try multiple phone number formats
        phone_formats = [self.phone, f"91{self.phone}", f"+91{self.phone}"]
        
        last_error = None
        for base_url in base_candidates:
            for phone_format in phone_formats:
                _LOGGER.info(f"📱 Trying base: {base_url}, phone format: {phone_format}")
                
                payload = {
                    "auth_id": phone_format,
                    "auth_type": 1,  # Critical: numeric, not "phone"
                    "password": self.password,
                }

                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        async with self.session.post(
                            f"{base_url}{LOGIN_ENDPOINT}",
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                                "X-APP-VER": "v4.11.4-133",
                                "X-OS-NAME": "Android",
                                "X-OS-VER": "v13-33",
                                "User-Agent": "com.bluestarindia.bluesmart",
                            },
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=30),
                        ) as response:
                            response_text = await response.text()
                            _LOGGER.info(f"API Response (attempt {attempt + 1}): {response.status} - {response_text}")
                            
                            if response.status == 200:
                                try:
                                    data = await response.json()
                                    self.session_token = data.get("session")
                                    
                                    # Initialize MQTT client with credentials
                                    await self._initialize_mqtt_client(data)
                                    
                                    _LOGGER.info("✅ Login successful")
                                    return data
                                    
                                except json.JSONDecodeError:
                                    _LOGGER.error(f"Invalid JSON response: {response_text}")
                                    last_error = BluestarAPIError("Invalid JSON response from server")
                                    continue
                            
                            elif response.status == 403:
                                _LOGGER.error("Access forbidden (403) - Check if account is locked or credentials are correct")
                                last_error = BluestarAPIError("Access forbidden - Account may be locked", response.status)
                                continue
                            
                            elif response.status == 401:
                                _LOGGER.error("Unauthorized (401) - Invalid credentials")
                                last_error = BluestarAPIError("Invalid credentials", response.status)
                                continue
                            
                            elif response.status == 502:
                                _LOGGER.warning(f"502 Internal Server Error (attempt {attempt + 1}/{max_retries})")
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                    continue
                                else:
                                    last_error = BluestarAPIError("API temporarily unavailable (502 error)", response.status)
                                    continue
                            
                            else:
                                _LOGGER.error(f"Unexpected response: {response.status} - {response_text}")
                                last_error = BluestarAPIError(f"Unexpected response: {response.status}", response.status)
                                continue
                    
                    except aiohttp.ClientError as err:
                        _LOGGER.error(f"Network error with phone {phone_format} (attempt {attempt + 1}): {err}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        else:
                            last_error = BluestarAPIError(f"Network error: {err}")
                            continue
        
        # If we get here, all attempts failed
        if last_error:
            raise last_error
        raise BluestarAPIError("Login failed with all phone number formats and base URLs")

    async def _initialize_mqtt_client(self, login_data: Dict[str, Any]) -> bool:
        """Initialize MQTT client with credentials from login response."""
        if not MQTT_AVAILABLE:
            _LOGGER.warning("⚠️ MQTT not available - using HTTP-only mode")
            return False
            
        try:
            # Extract credentials from login response
            credentials = self.credential_extractor.extract_credentials(login_data)
            
            # Disconnect existing client if any
            if self.mqtt_client:
                self.mqtt_client.disconnect()
            
            # Create new MQTT client
            self.mqtt_client = BluestarMQTTClient(credentials)
            
            # Connect to MQTT
            success = await self.mqtt_client.connect()
            
            if success:
                _LOGGER.info("✅ MQTT client initialized and connected")
                return True
            else:
                _LOGGER.warning("⚠️ MQTT client failed to connect")
                return False
                
        except Exception as error:
            _LOGGER.error(f"❌ Failed to initialize MQTT client: {error}")
            return False

    async def get_devices(self) -> Dict[str, Any]:
        """Get list of devices."""
        if not self.session_token:
            raise BluestarAPIError("Not authenticated. Call login() first.")

        headers = self._get_auth_headers()
        _LOGGER.info(f"Fetching devices with headers: {headers}")

        async with self.session.get(
            f"{self.base_url}{DEVICES_ENDPOINT}", headers=headers
        ) as response:
            if response.status == 401:
                _LOGGER.warning("Session expired, attempting re-login")
                await self.login()
                headers = self._get_auth_headers()
                async with self.session.get(
                    f"{self.base_url}{DEVICES_ENDPOINT}", headers=headers
                ) as retry_response:
                    if not retry_response.ok:
                        raise BluestarAPIError(
                            f"Failed to fetch devices: {retry_response.status}"
                        )
                    return await retry_response.json()

            if not response.ok:
                raise BluestarAPIError(f"Failed to fetch devices: {response.status}")

            data = await response.json()
            _LOGGER.info(f"Raw Bluestar response: {data}")
            return data

    async def control_device(self, device_id: str, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Control device using EXACT BLUESTAR CONTROL ALGORITHM."""
        if not self.session_token:
            raise BluestarAPIError("Not authenticated. Call login() first.")

        _LOGGER.info(f"🎛️ Control request for device: {device_id}")
        _LOGGER.info(f"Control data: {json.dumps(control_data, indent=2)}")

        headers = self._get_auth_headers()

        # EXACT BLUESTAR CONTROL ALGORITHM - DIRECT JSON STRUCTURE
        # Build the exact payload structure as used by the original app
        control_payload = {}
        
        # Add all control parameters directly (NOT nested under mode!)
        if control_data.get("pow") is not None:
            control_payload["pow"] = control_data["pow"]
        if control_data.get("mode") is not None:
            # EXACT MODE STRUCTURE from decompiled app
            control_payload["mode"] = {
                "value": int(control_data["mode"])
            }
        if control_data.get("stemp") is not None:
            control_payload["stemp"] = control_data["stemp"]
        if control_data.get("fspd") is not None:
            control_payload["fspd"] = control_data["fspd"]
        if control_data.get("vswing") is not None:
            control_payload["vswing"] = control_data["vswing"]
        if control_data.get("hswing") is not None:
            control_payload["hswing"] = control_data["hswing"]
        if control_data.get("display") is not None:
            control_payload["display"] = control_data["display"]

        # Add timestamp and source (EXACT APK FORMAT)
        control_payload["ts"] = int(asyncio.get_event_loop().time() * 1000)
        control_payload["src"] = "anmq"

        _LOGGER.info(f"📤 Step 1: Sending direct control via MQTT: {json.dumps(control_payload, indent=2)}")

        # EXACT BLUESTAR CONTROL ALGORITHM - MQTT PRIMARY METHOD
        control_result = None
        
        # Step 1: Try EXACT MQTT control (PRIMARY METHOD from decompiled app)
        if MQTT_AVAILABLE and self.mqtt_client and self.mqtt_client.is_connected:
            try:
                _LOGGER.info(f"📤 Step 1: Sending EXACT MQTT control: {json.dumps(control_payload, indent=2)}")
                
                # Use EXACT publish method from decompiled app
                success = self.mqtt_client.publish(device_id, control_payload)
                
                if success:
                    control_result = {"method": "EXACT_MQTT", "status": "success"}
                    _LOGGER.info("✅ EXACT MQTT control success")
                else:
                    _LOGGER.warning("⚠️ EXACT MQTT control failed")
            except Exception as error:
                _LOGGER.warning(f"⚠️ EXACT MQTT control failed: {error}")
        else:
            if not MQTT_AVAILABLE:
                _LOGGER.info("⚠️ MQTT not available, using HTTP API only")
            else:
                _LOGGER.warning("⚠️ EXACT MQTT client not available, trying HTTP API fallback")

        # Step 2: HTTP API fallback with EXACT MODE CONTROL MECHANISM
        if not control_result:
            try:
                _LOGGER.info(f"📤 Step 2: Sending control via HTTP API (EXACT MODE CONTROL): {json.dumps(control_payload, indent=2)}")
                
                # EXACT MODE CONTROL MECHANISM from decompiled app
                # Get current device state to determine the mode
                device_response = await self.session.get(f"{self.base_url}{DEVICES_ENDPOINT}", headers=headers)
                
                if not device_response.ok:
                    raise BluestarAPIError("Failed to fetch device state")
                
                device_data = await device_response.json()
                current_state = device_data.get("states", {}).get(device_id)
                
                if not current_state:
                    raise BluestarAPIError("Device not found")

                # Determine current mode (EXACT from decompiled app)
                current_mode = current_state.get("state", {}).get("mode", 2)
                
                # If mode is being changed, use the new mode (EXACT from decompiled app)
                if control_payload.get("mode") is not None:
                    # Handle both old format (direct value) and new format (nested with value)
                    if isinstance(control_payload["mode"], dict) and "value" in control_payload["mode"]:
                        current_mode = int(control_payload["mode"]["value"])
                    else:
                        current_mode = int(control_payload["mode"])

                # Build mode-specific preferences structure (EXACT from decompiled app)
                mode_config = {}
                
                # Add control parameters to mode configuration (EXACT from decompiled app)
                if control_payload.get("pow") is not None:
                    mode_config["power"] = str(control_payload["pow"])
                if control_payload.get("mode") is not None:
                    # Handle both old format (direct value) and new format (nested with value)
                    if isinstance(control_payload["mode"], dict) and "value" in control_payload["mode"]:
                        mode_config["mode"] = str(control_payload["mode"]["value"])
                    else:
                        mode_config["mode"] = str(control_payload["mode"])
                if control_payload.get("stemp") is not None:
                    mode_config["stemp"] = str(control_payload["stemp"])
                if control_payload.get("fspd") is not None:
                    mode_config["fspd"] = str(control_payload["fspd"])
                if control_payload.get("vswing") is not None:
                    mode_config["vswing"] = str(control_payload["vswing"])
                if control_payload.get("hswing") is not None:
                    mode_config["hswing"] = str(control_payload["hswing"])
                if control_payload.get("display") is not None:
                    mode_config["display"] = str(control_payload["display"])

                # EXACT NESTED STRUCTURE from decompiled app
                preferences_payload = {
                    "preferences": {
                        "mode": {
                            str(current_mode): mode_config
                        }
                    }
                }

                _LOGGER.info(f"📤 EXACT MODE CONTROL STRUCTURE: {json.dumps(preferences_payload, indent=2)}")

                preferences_response = await self.session.post(
                    f"{self.base_url}{PREFERENCES_ENDPOINT.format(device_id=device_id)}",
                    headers=headers,
                    json=preferences_payload
                )

                if preferences_response.ok:
                    control_result = await preferences_response.json()
                    _LOGGER.info(f"✅ EXACT MODE CONTROL success: {control_result}")
                else:
                    _LOGGER.warning("⚠️ EXACT MODE CONTROL failed, trying direct MQTT structure")
                    
                    # Fallback to direct MQTT structure
                    mqtt_style_payload = {
                        "state": {
                            "desired": control_payload
                        }
                    }
                    
                    state_response = await self.session.post(
                        f"{self.base_url}{STATE_ENDPOINT.format(device_id=device_id)}",
                        headers=headers,
                        json=mqtt_style_payload
                    )

                    if state_response.ok:
                        control_result = await state_response.json()
                        _LOGGER.info(f"✅ Direct MQTT structure success: {control_result}")
                    else:
                        _LOGGER.warning("⚠️ All control methods failed")
            except Exception as error:
                _LOGGER.warning(f"⚠️ EXACT MODE CONTROL failed: {error}")

        # Step 3: Force sync if all methods fail
        if not control_result:
            try:
                _LOGGER.info("📤 Step 3: Sending force sync")
                force_sync_payload = {"fpsh": 1}
                
                if MQTT_AVAILABLE and self.mqtt_client and self.mqtt_client.is_connected:
                    success = self.mqtt_client.force_sync(device_id)
                    if success:
                        _LOGGER.info("✅ Force sync via EXACT MQTT")
                else:
                    force_sync_response = await self.session.post(
                        f"{self.base_url}{CONTROL_ENDPOINT.format(device_id=device_id)}",
                        headers=headers,
                        json=force_sync_payload
                    )
                    
                    if force_sync_response.ok:
                        _LOGGER.info("✅ Force sync via HTTP")
                    else:
                        _LOGGER.warning("⚠️ Force sync failed")
            except Exception as error:
                _LOGGER.warning(f"⚠️ Force sync failed: {error}")

        # Get updated device state
        updated_device_response = await self.session.get(f"{self.base_url}{DEVICES_ENDPOINT}", headers=headers)
        updated_device_data = await updated_device_response.json()
        updated_state = updated_device_data.get("states", {}).get(device_id, {})
        
        state = {
            "power": updated_state.get("state", {}).get("pow") == 1,
            "mode": updated_state.get("state", {}).get("mode", 2),
            "temperature": updated_state.get("state", {}).get("stemp", "24"),
            "currentTemp": updated_state.get("state", {}).get("ctemp", "27.5"),
            "fanSpeed": updated_state.get("state", {}).get("fspd", 2),
            "swing": updated_state.get("state", {}).get("vswing") != 0,
            "display": updated_state.get("state", {}).get("display") != 0,
            "connected": updated_state.get("connected", False),
            "timestamp": int(asyncio.get_event_loop().time() * 1000),
            "rssi": updated_state.get("state", {}).get("rssi", -45),
            "error": updated_state.get("state", {}).get("err", 0),
            "source": updated_state.get("state", {}).get("src", "unknown")
        }

        return {
            "message": "Control command sent successfully",
            "deviceId": device_id,
            "controlData": control_data,
            "state": state,
            "method": "EXACT_BLUESTAR_CONTROL",
            "api": control_result
        }