"""Constants for the .be Domain Checker integration."""

DOMAIN = "be_domain_checker"

CONF_DOMAIN = "domain"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_UPDATE_INTERVAL = 60  # in minutes

# Custom events fired by the integration
EVENT_DOMAIN_AVAILABLE = "be_domain_checker_domain_available"
EVENT_STATUS_CHANGED = "be_domain_checker_status_changed"
