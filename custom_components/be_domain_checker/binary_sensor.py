"""Binary sensor platform for .be Domain Checker."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Set up the .be Domain Checker binary sensor platform."""
    coordinator: BeDomainCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BeDomainBinarySensor(coordinator)])


class BeDomainBinarySensor(CoordinatorEntity[BeDomainCoordinator], BinarySensorEntity):
    """Representation of a .be Domain Checker binary sensor."""

    def __init__(self, coordinator: BeDomainCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_name = f"{coordinator.domain_name} Available"
        self._attr_unique_id = f"{coordinator.domain_name}_available"

    @property
    def is_on(self) -> bool | None:
        """Return true if the domain is available."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("status") == "AVAILABLE"

    @property
    def icon(self) -> str:
        """Return the icon based on availability."""
        if self.is_on:
            return "mdi:web-plus"
        return "mdi:web"

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the state attributes."""
        return {
            "domain": self.coordinator.domain_name,
        }
