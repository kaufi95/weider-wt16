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

from .const import DOMAIN, CONF_MODBUS_ADDR, CONF_SCAN_INTERVAL, CONF_CREATE_DASHBOARD, DEFAULT_PORT, DEFAULT_MODBUS_ADDR, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_MODBUS_ADDR, default=DEFAULT_MODBUS_ADDR): vol.All(vol.Coerce(int), vol.Range(min=1, max=247)),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Weider WT16 Heat Pump."""

    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate ranges manually
            modbus_addr = user_input.get(CONF_MODBUS_ADDR, DEFAULT_MODBUS_ADDR)
            scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            
            if not (1 <= modbus_addr <= 247):
                errors[CONF_MODBUS_ADDR] = "Modbus address must be between 1 and 247"
            elif not (10 <= scan_interval <= 300):
                errors[CONF_SCAN_INTERVAL] = "Scan interval must be between 10 and 300 seconds"
            else:
                # Test the connection
                host = user_input[CONF_HOST]
                port = user_input.get(CONF_PORT, DEFAULT_PORT)

                try:
                    connection_result = await self._test_connection(host, port, modbus_addr)
                    if connection_result == "success":
                        # Store connection data for next step
                        self._connection_data = user_input
                        return await self.async_step_dashboard()
                    else:
                        errors["base"] = connection_result
                except Exception as err:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception during connection test: %s", err)
                    errors["base"] = "unknown"

        # Build schema dynamically to ensure all fields show
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_MODBUS_ADDR, default=DEFAULT_MODBUS_ADDR): vol.Coerce(int),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.Coerce(int),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_dashboard(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle dashboard installation step."""
        if user_input is not None:
            # Combine connection data with dashboard choice
            final_data = {**self._connection_data, **user_input}

            host = final_data[CONF_HOST]
            port = final_data[CONF_PORT]
            modbus_addr = final_data[CONF_MODBUS_ADDR]

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
        try:
            _LOGGER.info("Starting connection test for %s:%d (modbus addr %d)", host, port, modbus_addr)
            result = await self.hass.async_add_executor_job(self._test_connection_sync, host, port, modbus_addr)
            _LOGGER.info("Connection test result: %s", result)
            return result
        except Exception as err:
            _LOGGER.error("Error testing connection: %s", err, exc_info=True)
            return "unknown"

    def _test_connection_sync(self, host: str, port: int, modbus_addr: int) -> str:
        """Test connection synchronously."""
        _LOGGER.info("Testing connection to %s:%d", host, port)

        try:
            # Test pymodbus import first
            try:
                from pymodbus.client import ModbusTcpClient

                _LOGGER.info("PyModbus import successful")
            except ImportError as import_err:
                _LOGGER.error("Failed to import pymodbus: %s", import_err)
                return "unknown"

            # Create client with timeout
            _LOGGER.info("Creating ModbusTcpClient")
            client = ModbusTcpClient(host=host, port=port, timeout=5)

            _LOGGER.info("Attempting to connect...")
            if not client.connect():
                _LOGGER.error("Failed to connect to %s:%d", host, port)
                return "cannot_connect"

            _LOGGER.info("Connected successfully, testing register read...")

            # Test with a known working register
            result = client.read_input_registers(address=12, count=1, slave=modbus_addr)
            client.close()

            _LOGGER.info("Register read result: %s", result)

            if hasattr(result, "isError") and result.isError():
                _LOGGER.error("Modbus read error: %s", result)
                return "modbus_error"
            elif hasattr(result, "registers") and result.registers:
                _LOGGER.info("Success! Read value: %s", result.registers[0])
                return "success"
            else:
                _LOGGER.error("Unexpected result format: %s", result)
                return "modbus_error"

        except ConnectionRefusedError as err:
            _LOGGER.error("Connection refused: %s", err)
            return "connection_refused"
        except OSError as err:
            _LOGGER.error("OS Error: %s", err)
            if "timed out" in str(err).lower():
                return "timeout"
            elif "no route to host" in str(err).lower():
                return "no_route"
            else:
                return "network_error"
        except Exception as err:
            _LOGGER.error("Unexpected exception in connection test: %s", err, exc_info=True)
            return "unknown"
