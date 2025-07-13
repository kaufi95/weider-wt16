"""Binary sensor platform for Weider WT16 Heat Pump."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
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
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        WeiderWT16BinarySensor(coordinator, "stroemungswaechter_wp1", "Strömungswächter WP1", BinarySensorDeviceClass.MOTION),
        WeiderWT16BinarySensor(coordinator, "verdichter_wp1", "Verdichter WP1", BinarySensorDeviceClass.RUNNING),
        WeiderWT16BinarySensor(coordinator, "up_heizen_wp1", "UP-Heizen WP1", BinarySensorDeviceClass.RUNNING),
        WeiderWT16BinarySensor(coordinator, "up_sole_wasser_wp1", "UP-Sole/Wasser WP1", BinarySensorDeviceClass.RUNNING),
        WeiderWT16BinarySensor(coordinator, "up_mischer_1", "UP-Mischer 1", BinarySensorDeviceClass.RUNNING),
        WeiderWT16BinarySensor(coordinator, "up_warmwasser", "UP-Warmwasser", BinarySensorDeviceClass.RUNNING),
        WeiderWT16BinarySensor(coordinator, "fernstoerung", "Fernstörung", BinarySensorDeviceClass.PROBLEM),
        WeiderWT16BinarySensor(coordinator, "sperre_warmwasser", "Sperre Warmwasser", BinarySensorDeviceClass.LOCK),
        WeiderWT16BinarySensor(coordinator, "sperre_heizen", "Sperre Heizen", BinarySensorDeviceClass.LOCK),
        WeiderWT16BinarySensor(coordinator, "evu_sperre", "EVU-Sperre", BinarySensorDeviceClass.LOCK),
        WeiderWT16BinarySensor(coordinator, "sgready_1", "SGready 1", None),
        WeiderWT16BinarySensor(coordinator, "sgready_2", "SGready 2", None),
    ]

    async_add_entities(entities)


class WeiderWT16BinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Weider WT16 binary sensor."""

    def __init__(
        self,
        coordinator: WeiderWT16DataUpdateCoordinator,
        data_key: str,
        name: str,
        device_class: BinarySensorDeviceClass | None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_unique_id = f"weider_wt16_{data_key}"
        self._attr_entity_id = f"binary_sensor.{data_key}"
        self._attr_device_info = DEVICE_INFO

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get(self._data_key)
