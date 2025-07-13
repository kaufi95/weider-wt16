"""Data update coordinator for Weider WT16 Heat Pump."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta
from typing import Any

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, CONF_PORT, CONF_MODBUS_ADDR, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class WeiderWT16DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Weider WT16 heat pump."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.modbus_addr = entry.data.get(CONF_MODBUS_ADDR, 1)
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name="Weider WT16",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the heat pump."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Weider WT16: {err}") from err

    def _read_register_with_retry(self, client, reg_type: str, address: int, count: int = 1, retries: int = 2):
        """Read a register with retry logic for unstable connections."""
        for attempt in range(retries + 1):
            try:
                if reg_type == "discrete":
                    result = client.read_discrete_inputs(address=address, count=count, slave=self.modbus_addr)
                elif reg_type == "input":
                    result = client.read_input_registers(address=address, count=count, slave=self.modbus_addr)
                elif reg_type == "holding":
                    result = client.read_holding_registers(address=address, count=count, slave=self.modbus_addr)
                else:
                    return None

                if not result.isError():
                    return result
                else:
                    _LOGGER.debug("Register %d read attempt %d failed: %s", address, attempt + 1, result)

            except (OSError, ConnectionError, ModbusException) as err:
                if "broken pipe" in str(err).lower() or "connection" in str(err).lower():
                    _LOGGER.debug("Connection issue reading register %d (attempt %d): %s", address, attempt + 1, err)
                    if attempt < retries:
                        # Try to reconnect
                        try:
                            client.close()
                            time.sleep(0.1)  # Brief pause before retry
                            if not client.connect():
                                _LOGGER.debug("Reconnection failed for register %d", address)
                                continue
                        except Exception:
                            pass
                    else:
                        _LOGGER.warning("Failed to read register %d after %d attempts: %s", address, retries + 1, err)
                else:
                    _LOGGER.warning("Error reading register %d: %s", address, err)
                    break
        return None

    def _fetch_data(self) -> dict[str, Any]:
        """Fetch data from Modbus TCP with improved error handling."""
        data = {}

        try:
            client = ModbusTcpClient(host=self.host, port=self.port, timeout=10)

            if not client.connect():
                raise ModbusException(f"Unable to connect to {self.host}:{self.port}")

            _LOGGER.debug("Connected to heat pump, reading registers...")
            successful_reads = 0
            total_registers = 0

            # Read discrete inputs (binary sensors) - with German keys
            discrete_registers = [
                (45, "stroemungswaechter_wp1"),
                (679, "verdichter_wp1"),
                (680, "up_heizen_wp1"),
                (681, "up_sole_wasser_wp1"),
                (682, "up_mischer_1"),
                (685, "up_warmwasser"),
                (686, "fernstoerung"),
                (703, "sperre_warmwasser"),
                (704, "sperre_heizen"),
                (705, "evu_sperre"),
                (706, "sgready_1"),
                (707, "sgready_2"),
            ]

            for address, key in discrete_registers:
                total_registers += 1
                result = self._read_register_with_retry(client, "discrete", address)
                if result and hasattr(result, "bits"):
                    data[key] = result.bits[0]
                    successful_reads += 1

            # Read input registers (sensors) - with German keys
            input_registers = [
                # Verified working range 12-44
                (12, "raum_ist_temperatur", 0.1),
                (13, "warmwasser_ist_temperatur", 0.1),
                (14, "vorlauf_soll_temperatur", 0.1),
                (15, "aussentemperatur", 0.1),
                (16, "puffer_ist_temperatur", 0.1),
                (17, "mischer_ist_temperatur", 0.1),
                (18, "reservefuehler_1_temperatur", 0.1),
                (19, "reservefuehler_2_temperatur", 0.1),
                (20, "reservefuehler_3_temperatur", 0.1),
                (21, "abtaufuehler_ist_temperatur", 0.1),
                (25, "wp1_vorlauf_ist_temperatur", 0.1),
                (26, "wp1_ruecklauf_ist_temperatur", 0.1),
                (27, "wp1_quelle_eintritt_temperatur", 0.1),
                (28, "wp1_quelle_austritt_temperatur", 0.1),
                (29, "wp1_ueberhitzung", 0.1),
                (31, "wp1_verdampfungstemperatur", 0.1),
                (33, "wp1_verfluessigungstemperatur", 0.1),
                (35, "wp1_verdampfer_temperatur", 0.1),
                (36, "wp1_sauggas_temperatur", 0.1),
                (37, "wp1_heissgas_temperatur", 0.1),
                (38, "wp1_sauggas_evi_temperatur", 0.1),
                (40, "wp1_verdampfungstemperatur_evi", 0.1),
                (42, "wp1_verfluessigungstemperatur_evi", 0.1),
                (43, "wp1_verfluessigungsdruck_evi", 0.01),
                (44, "wp1_volumenstrom", 1),
                (46, "wp1_ueberhitzung_evi", 0.1),
                (726, "mlt1_vorlauf_soll_temperatur", 0.1),
                (727, "mlt1_vorlauf_ist_temperatur", 0.1),
                (736, "mlt1_mischerposition", 1),
                (1008, "aktuelle_schritte_cl1", 1),
                (1048, "aktuelle_schritte_cl2", 1),
            ]

            for address, key, scale in input_registers:
                total_registers += 1
                result = self._read_register_with_retry(client, "input", address)
                if result and hasattr(result, "registers"):
                    data[key] = result.registers[0] * scale
                    successful_reads += 1

            # Read holding registers (setpoints) - with German keys
            holding_registers = [
                (1, "warmwasser_soll_temperatur", 0.1),
                (723, "raum_soll_temperatur", 0.1),
            ]

            for address, key, scale in holding_registers:
                total_registers += 1
                result = self._read_register_with_retry(client, "holding", address)
                if result and hasattr(result, "registers"):
                    data[key] = result.registers[0] * scale
                    successful_reads += 1

            # Read runtime data (32-bit values) - with German keys
            runtime_registers = [
                (60164, "wp1_letzte_laufzeit_pumpe"),
                (60168, "wp1_letzte_laufzeit_warmwasser"),
            ]
            
            for address, key in runtime_registers:
                total_registers += 1
                result = self._read_register_with_retry(client, "input", address, count=2)
                if result and hasattr(result, 'registers') and len(result.registers) >= 2:
                    # Combine two 16-bit registers into 32-bit value (word swapped)
                    data[key] = (result.registers[1] << 16) | result.registers[0]
                    successful_reads += 1

            # Read error message register (string - 16 registers)
            total_registers += 1
            result = self._read_register_with_retry(client, "input", 63000, count=16)
            if result and hasattr(result, 'registers') and len(result.registers) >= 16:
                # Convert registers to string (2 bytes per register)
                text_bytes = []
                for reg in result.registers:
                    text_bytes.append((reg >> 8) & 0xFF)  # High byte
                    text_bytes.append(reg & 0xFF)         # Low byte
                
                # Convert bytes to string, removing null terminators
                try:
                    error_text = bytes(text_bytes).decode('utf-8', errors='ignore').rstrip('\x00')
                    data["aktive_fehlermeldung"] = error_text if error_text else "Keine Fehlermeldung"
                except:
                    data["aktive_fehlermeldung"] = "Fehler beim Lesen"
                successful_reads += 1

            client.close()

            # Log success rate
            success_rate = (successful_reads / total_registers * 100) if total_registers > 0 else 0
            if success_rate < 80:
                _LOGGER.warning("Low success rate reading registers: %.1f%% (%d/%d)", success_rate, successful_reads, total_registers)
            else:
                _LOGGER.debug("Successfully read %.1f%% of registers (%d/%d)", success_rate, successful_reads, total_registers)

            # Raise error if we couldn't read any critical registers
            if successful_reads == 0:
                raise ModbusException("Failed to read any registers from heat pump")

            return data

        except Exception as err:
            try:
                client.close()
            except:
                pass
            raise

    async def async_write_register(self, address: int, value: int) -> bool:
        """Write to a holding register."""
        try:
            return await self.hass.async_add_executor_job(self._write_register, address, value)
        except Exception as err:
            _LOGGER.error("Error writing to register %d: %s", address, err)
            return False

    def _write_register(self, address: int, value: int) -> bool:
        """Write to a holding register synchronously with retry logic."""
        retries = 2
        for attempt in range(retries + 1):
            try:
                client = ModbusTcpClient(host=self.host, port=self.port, timeout=5)
                if not client.connect():
                    _LOGGER.debug("Write connection attempt %d failed", attempt + 1)
                    if attempt < retries:
                        time.sleep(0.1)
                        continue
                    return False

                result = client.write_register(address=address, value=value, slave=self.modbus_addr)
                client.close()

                if not result.isError():
                    return True
                else:
                    _LOGGER.debug("Write attempt %d failed: %s", attempt + 1, result)

            except (OSError, ConnectionError, ModbusException) as err:
                if "broken pipe" in str(err).lower() or "connection" in str(err).lower():
                    _LOGGER.debug("Connection issue writing register %d (attempt %d): %s", address, attempt + 1, err)
                    if attempt < retries:
                        time.sleep(0.1)
                        continue
                else:
                    _LOGGER.error("Error writing register %d: %s", address, err)
                    break
            except Exception as err:
                _LOGGER.error("Unexpected error writing register %d: %s", address, err)
                break

        return False