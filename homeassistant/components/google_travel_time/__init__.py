"""The google_travel_time component."""

import logging

from google.api_core.client_options import ClientOptions
from google.maps.routing_v2 import RoutesAsyncClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import CONF_DESTINATION, CONF_ORIGIN, CONF_TIME
from .coordinator import GoogleTravelTimeCoordinator

PLATFORMS = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Google Maps Travel Time from a config entry."""
    api_key = config_entry.data[CONF_API_KEY]
    origin = config_entry.data[CONF_ORIGIN]
    destination = config_entry.data[CONF_DESTINATION]

    client_options = ClientOptions(api_key=api_key)
    client = RoutesAsyncClient(client_options=client_options)

    coordinator = GoogleTravelTimeCoordinator(
        hass, config_entry, origin, destination, client
    )
    config_entry.runtime_data = coordinator

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate an old config entry."""

    if config_entry.version == 1:
        _LOGGER.debug(
            "Migrating from version %s.%s",
            config_entry.version,
            config_entry.minor_version,
        )
        options = dict(config_entry.options)
        if options.get(CONF_TIME) == "now":
            options[CONF_TIME] = None
        elif options.get(CONF_TIME) is not None:
            if dt_util.parse_time(options[CONF_TIME]) is None:
                try:
                    from_timestamp = dt_util.utc_from_timestamp(int(options[CONF_TIME]))
                    options[CONF_TIME] = (
                        f"{from_timestamp.time().hour:02}:{from_timestamp.time().minute:02}"
                    )
                except ValueError:
                    _LOGGER.error(
                        "Invalid time format found while migrating: %s. The old config never worked. Reset to default (empty)",
                        options[CONF_TIME],
                    )
                    options[CONF_TIME] = None
        hass.config_entries.async_update_entry(config_entry, options=options, version=2)
        _LOGGER.debug(
            "Migration to version %s.%s successful",
            config_entry.version,
            config_entry.minor_version,
        )
    return True
