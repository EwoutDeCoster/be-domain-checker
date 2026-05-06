"""Sensor platform for .be Domain Checker."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .__init__ import BeDomainCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the .be Domain Checker sensor platform."""
    coordinator: BeDomainCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BeDomainSensor(coordinator)])


class BeDomainSensor(CoordinatorEntity[BeDomainCoordinator], SensorEntity):
    """Representation of a .be Domain Checker sensor."""

    _attr_icon = "mdi:dns"
    _attr_force_update = True

    def __init__(self, coordinator: BeDomainCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"{coordinator.domain_name} Status"
        self._attr_unique_id = f"{coordinator.domain_name}_status"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("status")

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {"domain": self.coordinator.domain_name}
        return {
            "domain": self.coordinator.domain_name,
            "last_checked": self.coordinator.data.get("last_checked"),
        }
