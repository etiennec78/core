"""The Google Travel Time data coordinator."""

import datetime
import logging
from typing import TYPE_CHECKING

from google.api_core.exceptions import GoogleAPIError, PermissionDenied
from google.maps.routing_v2 import (
    ComputeRoutesRequest,
    Route,
    RouteModifiers,
    RoutesAsyncClient,
    RouteTravelMode,
    RoutingPreference,
    TransitPreferences,
)
from google.protobuf import timestamp_pb2

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LANGUAGE, CONF_MODE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.location import find_coordinates
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ARRIVAL_TIME,
    CONF_AVOID,
    CONF_DEPARTURE_TIME,
    CONF_TRAFFIC_MODEL,
    CONF_TRANSIT_MODE,
    CONF_TRANSIT_ROUTING_PREFERENCE,
    CONF_UNITS,
    DOMAIN,
    TRAFFIC_MODELS_TO_GOOGLE_SDK_ENUM,
    TRANSIT_PREFS_TO_GOOGLE_SDK_ENUM,
    TRANSPORT_TYPES_TO_GOOGLE_SDK_ENUM,
    TRAVEL_MODES_TO_GOOGLE_SDK_ENUM,
    UNITS_TO_GOOGLE_SDK_ENUM,
)
from .helpers import (
    convert_to_waypoint,
    create_routes_api_disabled_issue,
    delete_routes_api_disabled_issue,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=10)
FIELD_MASK = "routes.duration,routes.localized_values"


def convert_time(time_str: str) -> timestamp_pb2.Timestamp | None:
    """Convert a string like '08:00' to a google pb2 Timestamp.

    If the time is in the past, it will be shifted to the next day.
    """
    parsed_time = dt_util.parse_time(time_str)
    if TYPE_CHECKING:
        assert parsed_time is not None
    start_of_day = dt_util.start_of_local_day()
    combined = datetime.datetime.combine(
        start_of_day,
        parsed_time,
        start_of_day.tzinfo,
    )
    if combined < dt_util.now():
        combined = combined + datetime.timedelta(days=1)
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(dt=combined)
    return timestamp


class GoogleTravelTimeCoordinator(DataUpdateCoordinator[Route]):
    """Google Travel Time DataUpdateCoordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        origin: str,
        destination: str,
        client: RoutesAsyncClient,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=SCAN_INTERVAL,
        )
        self._client = client
        self._config_entry = config_entry
        self._origin = origin
        self._destination = destination
        self.resolved_origin: str | None = None
        self.resolved_destination: str | None = None

    async def _async_update_data(self) -> Route:
        """Get the latest data from Google."""
        travel_mode = TRAVEL_MODES_TO_GOOGLE_SDK_ENUM[
            self._config_entry.options[CONF_MODE]
        ]

        if (
            departure_time := self._config_entry.options.get(CONF_DEPARTURE_TIME)
        ) is not None:
            departure_time = convert_time(departure_time)

        if (
            arrival_time := self._config_entry.options.get(CONF_ARRIVAL_TIME)
        ) is not None:
            arrival_time = convert_time(arrival_time)
        if travel_mode != RouteTravelMode.TRANSIT:
            arrival_time = None

        traffic_model = None
        routing_preference = None
        route_modifiers = None
        if travel_mode == RouteTravelMode.DRIVE:
            if (
                options_traffic_model := self._config_entry.options.get(
                    CONF_TRAFFIC_MODEL
                )
            ) is not None:
                traffic_model = TRAFFIC_MODELS_TO_GOOGLE_SDK_ENUM[options_traffic_model]
            routing_preference = RoutingPreference.TRAFFIC_AWARE_OPTIMAL
            route_modifiers = RouteModifiers(
                avoid_tolls=self._config_entry.options.get(CONF_AVOID) == "tolls",
                avoid_ferries=self._config_entry.options.get(CONF_AVOID) == "ferries",
                avoid_highways=self._config_entry.options.get(CONF_AVOID) == "highways",
                avoid_indoor=self._config_entry.options.get(CONF_AVOID) == "indoor",
            )

        transit_preferences = None
        if travel_mode == RouteTravelMode.TRANSIT:
            transit_routing_preference = None
            transit_travel_mode = (
                TransitPreferences.TransitTravelMode.TRANSIT_TRAVEL_MODE_UNSPECIFIED
            )
            if (
                option_transit_preferences := self._config_entry.options.get(
                    CONF_TRANSIT_ROUTING_PREFERENCE
                )
            ) is not None:
                transit_routing_preference = TRANSIT_PREFS_TO_GOOGLE_SDK_ENUM[
                    option_transit_preferences
                ]
            if (
                option_transit_mode := self._config_entry.options.get(CONF_TRANSIT_MODE)
            ) is not None:
                transit_travel_mode = TRANSPORT_TYPES_TO_GOOGLE_SDK_ENUM[
                    option_transit_mode
                ]
            transit_preferences = TransitPreferences(
                routing_preference=transit_routing_preference,
                allowed_travel_modes=[transit_travel_mode],
            )

        language = None
        if (
            options_language := self._config_entry.options.get(CONF_LANGUAGE)
        ) is not None:
            language = options_language

        self.resolved_origin = find_coordinates(self.hass, self._origin)
        self.resolved_destination = find_coordinates(self.hass, self._destination)
        _LOGGER.debug(
            "Getting update for origin: %s destination: %s",
            self.resolved_origin,
            self.resolved_destination,
        )

        if self.resolved_destination is None or self.resolved_origin is None:
            raise UpdateFailed("Could not resolve origin or destination coordinates.")

        request = ComputeRoutesRequest(
            origin=convert_to_waypoint(self.hass, self.resolved_origin),
            destination=convert_to_waypoint(self.hass, self.resolved_destination),
            travel_mode=travel_mode,
            routing_preference=routing_preference,
            departure_time=departure_time,
            arrival_time=arrival_time,
            route_modifiers=route_modifiers,
            language_code=language,
            units=UNITS_TO_GOOGLE_SDK_ENUM[self._config_entry.options[CONF_UNITS]],
            traffic_model=traffic_model,
            transit_preferences=transit_preferences,
        )
        try:
            response = await self._client.compute_routes(
                request, metadata=[("x-goog-fieldmask", FIELD_MASK)]
            )
            _LOGGER.debug("Received response: %s", response)
            if response is None or len(response.routes) < 1:
                raise UpdateFailed(
                    "No routes found for the given origin and destination."
                )

            delete_routes_api_disabled_issue(self.hass, self._config_entry)
            return response.routes[0]

        except PermissionDenied as ex:
            create_routes_api_disabled_issue(self.hass, self._config_entry)
            raise UpdateFailed("Routes API is disabled for this API key") from ex
        except GoogleAPIError as ex:
            raise UpdateFailed(f"Error getting travel time: {ex}") from ex
