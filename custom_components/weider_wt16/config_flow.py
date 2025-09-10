"""Config flow for Weider WT16 Heat Pump integration."""

from __future__ import annotations

import logging
from typing import Any

import socket
import voluptuous as vol
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_SCAN_INTERVAL,
    CONF_CREATE_DASHBOARD,
    CONF_ERROR_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_ERROR_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Weider WT16 Heat Pump."""

    VERSION = 3

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            connection_result = await self._test_user_connection(user_input)
            if connection_result == "success":
                self._connection_data = user_input
                return await self.async_step_dashboard()
            errors["base"] = connection_result

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_user_schema(),
            errors=errors,
        )

    async def _test_user_connection(self, user_input: dict[str, Any]) -> str:
        """Test connection with user input."""
        host = user_input[CONF_HOST]
        port = user_input.get(CONF_PORT, DEFAULT_PORT)
        modbus_addr = 1  # Hardcoded to 1

        try:
            return await self._test_connection(host, port, modbus_addr)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception during connection test: %s", err)
            return "unknown"

    def _get_user_schema(self) -> vol.Schema:
        """Get the user input schema."""
        return vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=15, max=300)),
                vol.Optional(CONF_ERROR_TIMEOUT, default=DEFAULT_ERROR_TIMEOUT): vol.All(vol.Coerce(int), vol.Range(min=60, max=600)),
            }
        )

    async def async_step_dashboard(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle dashboard installation step."""
        if user_input is not None:
            # Combine connection data with dashboard choice
            final_data = {**self._connection_data, **user_input}

            host = final_data[CONF_HOST]
            port = final_data[CONF_PORT]
            modbus_addr = 1  # Hardcoded to 1

            await self.async_set_unique_id(f"{host}_{port}_{modbus_addr}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Weider WT16 ({host})",
                data=final_data,
            )

        # Show dashboard installation form
        dashboard_schema = vol.Schema(
            {
                vol.Optional(CONF_CREATE_DASHBOARD, default=True): bool,
            }
        )

        return self.async_show_form(
            step_id="dashboard",
            data_schema=dashboard_schema,
            description_placeholders={
                "dashboard_info": "Dies erstellt einen 'Wärmepumpe' Tab mit Thermostaten zur Temperaturregelung und Diagrammen für Temperaturverläufe."
            },
        )

    async def _test_connection(self, host: str, port: int, modbus_addr: int) -> str:
        """Test if we can connect to the device."""

        def test_sync():
            try:
                client = ModbusTcpClient(host=host, port=port, timeout=5)
                if not client.connect():
                    return "cannot_connect"

                # Simple register read test
                result = client.read_input_registers(address=12, count=1)
                client.close()

                if hasattr(result, "isError") and result.isError():
                    return "modbus_error"
                elif hasattr(result, "registers"):
                    return "success"
                else:
                    return "modbus_error"

            except ConnectionRefusedError:
                return "connection_refused"
            except OSError as err:
                if "timed out" in str(err).lower():
                    return "timeout"
                return "network_error"
            except Exception:
                return "unknown"

        return await self.hass.async_add_executor_job(test_sync)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Weider WT16 Heat Pump."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current values from config entry
        current_scan_interval = self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        current_error_timeout = self.config_entry.data.get(CONF_ERROR_TIMEOUT, DEFAULT_ERROR_TIMEOUT)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SCAN_INTERVAL, default=current_scan_interval): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
                    vol.Optional(CONF_ERROR_TIMEOUT, default=current_error_timeout): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
                }
            ),
            errors={},
        )
