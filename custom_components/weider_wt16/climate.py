"""Climate platform for Weider WT16 Heat Pump."""

from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEVICE_INFO
from .coordinator import WeiderWT16DataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        WeiderWT16Climate(
            coordinator, "warmwasser_temperatur", "Warmwasser Temperatur", "warmwasser_ist_temperatur", "warmwasser_soll_temperatur", 1, 35, 60, 0.5
        ),
        WeiderWT16Climate(coordinator, "raum_soll_temperatur", "Raum Soll-Temperatur", "raum_ist_temperatur", "raum_soll_temperatur", 723, 15, 25, 0.5),
    ]

    async_add_entities(entities)


class WeiderWT16Climate(CoordinatorEntity, ClimateEntity):
    """Representation of a Weider WT16 climate entity."""

    def __init__(
        self,
        coordinator: WeiderWT16DataUpdateCoordinator,
        entity_type: str,
        name: str,
        temp_sensor_key: str,
        temp_setpoint_key: str,
        setpoint_register: int,
        min_temp: float,
        max_temp: float,
        temp_step: float,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._entity_type = entity_type
        self._temp_sensor_key = temp_sensor_key
        self._temp_setpoint_key = temp_setpoint_key
        self._setpoint_register = setpoint_register
        self._attr_name = name
        self._attr_unique_id = f"weider_wt16_climate_{entity_type}"
        self._attr_entity_id = f"climate.{entity_type}"
        self._attr_device_info = DEVICE_INFO
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_min_temp = min_temp
        self._attr_max_temp = max_temp
        self._attr_target_temperature_step = temp_step
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_hvac_modes = [HVACMode.AUTO]

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.get(self._temp_sensor_key)

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.coordinator.data.get(self._temp_setpoint_key)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation ie. heat, cool, idle."""
        return HVACMode.AUTO

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        if "temperature" in kwargs:
            temp = kwargs["temperature"]
            # Convert to register value (multiply by 10 for 0.1 scale)
            register_value = int(temp * 10)
            await self.coordinator.async_write_register(self._setpoint_register, register_value)
            await self.coordinator.async_request_refresh()
