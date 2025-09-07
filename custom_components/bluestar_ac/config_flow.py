"""Config flow for Bluestar Smart AC integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import BluestarAPI, BluestarAPIError
from .const import (
    CONF_BASE_URL,
    CONF_PASSWORD,
    CONF_PHONE,
    DEFAULT_BASE_URL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PHONE): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
    }
)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    _LOGGER.debug("CF1 validate_input() start")
    
    api = BluestarAPI(
        phone=data[CONF_PHONE],
        password=data[CONF_PASSWORD],
        base_url=data[CONF_BASE_URL],
    )
    _LOGGER.debug("CF2 API client created")

    try:
        _LOGGER.debug("CF3 entering async context manager")
        async with api as api_client:
            _LOGGER.info("Attempting to connect to Bluestar API...")
            _LOGGER.debug("CF4 calling login()")
            await api_client.login()
            _LOGGER.info("Login successful, fetching devices...")
            _LOGGER.debug("CF5 calling get_devices()")
            devices_data = await api_client.get_devices()
            _LOGGER.debug("CF6 got devices data")
            
            # Extract device information
            devices = devices_data.get("things", [])
            if not devices:
                _LOGGER.error("CF7 no devices found")
                raise CannotConnect("No devices found")
            
            # Determine connection method for title
            connection_method = "Standalone (MQTT + API)"
            
            _LOGGER.info(f"Found {len(devices)} devices")
            _LOGGER.debug("CF8 validation successful")
            return {
                "title": f"Bluestar Smart AC ({len(devices)} devices) - {connection_method}",
                "devices": devices,
            }
    except BluestarAPIError as err:
        _LOGGER.error(f"CF9 Bluestar API error: {err}")
        if "Invalid credentials" in str(err) or "401" in str(err):
            raise InvalidAuth("Invalid credentials. Please check your phone number and password.")
        elif "403" in str(err):
            raise InvalidAuth("Access forbidden. Your account may be restricted.")
        elif "502" in str(err) or "API temporarily unavailable" in str(err):
            raise CannotConnect("The Bluestar API is currently experiencing issues. Please try again in a few minutes. The official app may still work due to cached credentials.")
        elif "Login failed with all phone number formats" in str(err):
            raise InvalidAuth("Login failed. Please verify your phone number and password.")
        else:
            raise CannotConnect(f"Unable to connect to Bluestar API: {err}")
    except Exception as err:
        _LOGGER.error(f"CF10 Unexpected error during validation: {err}")
        raise CannotConnect(f"Unexpected error: {err}")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bluestar Smart AC."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Check if already configured
                await self.async_set_unique_id(user_input[CONF_PHONE])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, import_data: Dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_data)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Bluestar Smart AC."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_BASE_URL,
                        default=self.config_entry.options.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                    ): str,
                }
            ),
        )
