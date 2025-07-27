"""Sensor platform for Weider WT16 Heat Pump."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfVolumeFlowRate,
    UnitOfTime,
    PERCENTAGE,
)
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
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        WeiderWT16Sensor(
            coordinator, "raum_ist_temperatur", "Raum Ist-Temperatur", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT
        ),
        WeiderWT16Sensor(
            coordinator,
            "warmwasser_ist_temperatur",
            "Warmwasser Ist-Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "vorlauf_soll_temperatur",
            "Vorlauf Soll-Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator, "aussentemperatur", "Außentemperatur", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT
        ),
        WeiderWT16Sensor(
            coordinator,
            "puffer_ist_temperatur",
            "Puffer Ist-Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "mischer_ist_temperatur",
            "Mischer Ist-Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "abtaufuehler_ist_temperatur",
            "Abtaufühler Ist-Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_vorlauf_ist_temperatur",
            "WP1 Vorlauf Ist-Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_ruecklauf_ist_temperatur",
            "WP1 Rücklauf Ist-Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_quelle_eintritt_temperatur",
            "WP1 Quelle Eintritt Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_quelle_austritt_temperatur",
            "WP1 Quelle Austritt Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator, "wp1_ueberhitzung", "WP1 Überhitzung", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_verdampfungstemperatur",
            "WP1 Verdampfungstemperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_verfluessigungstemperatur",
            "WP1 Verflüssigungstemperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_verdampfer_temperatur",
            "WP1 Verdampfer Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_sauggas_temperatur",
            "WP1 Sauggas Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_heissgas_temperatur",
            "WP1 Heißgas Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_sauggas_evi_temperatur",
            "WP1 Sauggas EVI Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_verdampfungstemperatur_evi",
            "WP1 Verdampfungstemperatur EVI",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_verfluessigungstemperatur_evi",
            "WP1 Verflüssigungstemperatur EVI",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "wp1_verfluessigungsdruck_evi",
            "WP1 Verflüssigungsdruck EVI",
            UnitOfPressure.BAR,
            SensorDeviceClass.PRESSURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(coordinator, "wp1_volumenstrom", "WP1 Volumenstrom", UnitOfVolumeFlowRate.LITERS_PER_MINUTE, None, SensorStateClass.MEASUREMENT),
        WeiderWT16Sensor(
            coordinator, "wp1_ueberhitzung_evi", "WP1 Überhitzung EVI", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT
        ),
        WeiderWT16Sensor(
            coordinator,
            "mlt1_vorlauf_soll_temperatur",
            "MLT1 Vorlauf Soll-Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "mlt1_vorlauf_ist_temperatur",
            "MLT1 Vorlauf Ist-Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(coordinator, "mlt1_mischerposition", "MLT1 Mischerposition", "s", None, SensorStateClass.MEASUREMENT),
        WeiderWT16Sensor(coordinator, "aktuelle_schritte_cl1", "Aktuelle Schritte CL1", None, None, SensorStateClass.MEASUREMENT),
        WeiderWT16Sensor(coordinator, "aktuelle_schritte_cl2", "Aktuelle Schritte CL2", None, None, SensorStateClass.MEASUREMENT),
        WeiderWT16Sensor(
            coordinator,
            "reservefuehler_1_temperatur",
            "Reservefühler 1 Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "reservefuehler_2_temperatur",
            "Reservefühler 2 Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "reservefuehler_3_temperatur",
            "Reservefühler 3 Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(coordinator, "wp1_letzte_laufzeit_pumpe", "WP1 Letzte Laufzeit Pumpe", UnitOfTime.MINUTES, None, SensorStateClass.TOTAL_INCREASING),
        WeiderWT16Sensor(
            coordinator, "wp1_letzte_laufzeit_warmwasser", "WP1 Letzte Laufzeit Warmwasser", UnitOfTime.MINUTES, None, SensorStateClass.TOTAL_INCREASING
        ),
        WeiderWT16Sensor(
            coordinator, "raum_soll_temperatur", "Raum-Soll-Temperatur", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT
        ),
        WeiderWT16Sensor(
            coordinator,
            "warmwasser_soll_temperatur",
            "Warmwasser-Soll-Temperatur",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        WeiderWT16Sensor(
            coordinator,
            "aktive_fehlermeldung",
            "Aktive Fehlermeldung",
            None,
            None,
            None,
        ),
    ]

    async_add_entities(entities)


class WeiderWT16Sensor(CoordinatorEntity, SensorEntity):
    """Representation of a Weider WT16 sensor."""

    def __init__(
        self,
        coordinator: WeiderWT16DataUpdateCoordinator,
        data_key: str,
        name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_unique_id = f"weider_wt16_{data_key}"
        self._attr_entity_id = f"sensor.{data_key}"
        self._attr_device_info = DEVICE_INFO

    @property
    def native_value(self) -> float | int | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._data_key)
