"""The .be Domain Checker integration."""
from __future__ import annotations

from datetime import timedelta
import logging
import socket

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .const import (
    DOMAIN,
    CONF_DOMAIN,
    CONF_UPDATE_INTERVAL,
    EVENT_DOMAIN_AVAILABLE,
    EVENT_STATUS_CHANGED,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


def check_be_domain(domain: str) -> str:
    """Check the status of a .be domain by querying whois.dns.be on port 43."""
    domain = domain.strip().lower()
    if not domain.endswith(".be"):
        domain = f"{domain}.be"

    _LOGGER.debug("Querying WHOIS for domain %s", domain)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect(("whois.dns.be", 43))
        s.sendall(f"{domain}\r\n".encode("utf-8"))

        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        s.close()

        decoded_response = response.decode("utf-8", errors="ignore")

        # Parse the status from the response
        # Typically looking for a line starting with 'Status:' (case-insensitive)
        for line in decoded_response.splitlines():
            line_stripped = line.strip()
            if line_stripped.lower().startswith("status:"):
                parts = line_stripped.split(":", 1)
                if len(parts) > 1:
                    status = parts[1].strip().upper()
                    return status

        # If Status: line is not found, fallback to searching for keywords
        if "AVAILABLE" in decoded_response.upper():
            return "AVAILABLE"
        if "NOT AVAILABLE" in decoded_response.upper() or "REGISTERED" in decoded_response.upper():
            return "NOT AVAILABLE"

        return "UNKNOWN"
    except Exception as e:
        _LOGGER.error("Error querying WHOIS for %s: %s", domain, e)
        raise e


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up .be Domain Checker from a config entry."""
    domain = entry.data[CONF_DOMAIN]
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, 60)

    coordinator = BeDomainCoordinator(hass, entry, domain, update_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class BeDomainCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Class to manage fetching .be domain status."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        domain_name: str,
        update_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        self.domain_name = domain_name.strip().lower()
        if not self.domain_name.endswith(".be"):
            self.domain_name = f"{self.domain_name}.be"
        self.entry = entry
        self.last_status: str | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=f"be_domain_{self.domain_name}",
            update_interval=timedelta(minutes=update_interval),
        )

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch domain status using executor thread pool."""
        try:
            status = await self.hass.async_add_executor_job(
                check_be_domain, self.domain_name
            )

            # Fire events on change or availability
            if self.last_status is not None and self.last_status != status:
                _LOGGER.info(
                    "Domain %s changed status from %s to %s",
                    self.domain_name,
                    self.last_status,
                    status,
                )
                self.hass.bus.async_fire(
                    EVENT_STATUS_CHANGED,
                    {
                        "domain": self.domain_name,
                        "old_status": self.last_status,
                        "new_status": status,
                    },
                )

            if status == "AVAILABLE":
                _LOGGER.warning("Domain %s is AVAILABLE!", self.domain_name)
                self.hass.bus.async_fire(
                    EVENT_DOMAIN_AVAILABLE,
                    {
                        "domain": self.domain_name,
                        "status": status,
                    },
                )

            self.last_status = status
            return {
                "status": status,
                "domain": self.domain_name,
                "last_checked": dt_util.utcnow().isoformat(),
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with WHOIS server: {err}")
