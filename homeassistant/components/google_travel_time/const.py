"""Constants for Google Travel Time."""

from typing import Final

from google.maps.routing_v2 import (
    RouteTravelMode,
    TrafficModel,
    TransitPreferences,
    Units,
)

DOMAIN = "google_travel_time"

ATTRIBUTION = "Powered by Google"

CONF_DESTINATION = "destination"
CONF_OPTIONS = "options"
CONF_ORIGIN = "origin"
CONF_AVOID = "avoid"
CONF_UNITS = "units"
CONF_ARRIVAL_TIME = "arrival_time"
CONF_DEPARTURE_TIME = "departure_time"
CONF_TRAFFIC_MODEL = "traffic_model"
CONF_TRANSIT_MODE = "transit_mode"
CONF_TRANSIT_ROUTING_PREFERENCE = "transit_routing_preference"
CONF_TIME_TYPE = "time_type"
CONF_TIME = "time"

ARRIVAL_TIME = "Arrival Time"
DEPARTURE_TIME = "Departure Time"
TIME_TYPES = [ARRIVAL_TIME, DEPARTURE_TIME]

DEFAULT_NAME = "Google Travel Time"

ALL_LANGUAGES = [
    "ar",
    "bg",
    "bn",
    "ca",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "eu",
    "fa",
    "fi",
    "fr",
    "gl",
    "gu",
    "hi",
    "hr",
    "hu",
    "id",
    "it",
    "iw",
    "ja",
    "kn",
    "ko",
    "lt",
    "lv",
    "ml",
    "mr",
    "nl",
    "no",
    "pl",
    "pt",
    "pt-BR",
    "pt-PT",
    "ro",
    "ru",
    "sk",
    "sl",
    "sr",
    "sv",
    "ta",
    "te",  # codespell:ignore te
    "th",
    "tl",
    "tr",
    "uk",
    "vi",
    "zh-CN",
    "zh-TW",
]

AVOID_OPTIONS = ["tolls", "highways", "ferries", "indoor"]

TRANSIT_PREFS = ["less_walking", "fewer_transfers"]
TRANSIT_PREFS_TO_GOOGLE_SDK_ENUM = {
    "less_walking": TransitPreferences.TransitRoutingPreference.LESS_WALKING,
    "fewer_transfers": TransitPreferences.TransitRoutingPreference.FEWER_TRANSFERS,
}

TRANSPORT_TYPES = ["bus", "subway", "train", "tram", "rail"]
TRANSPORT_TYPES_TO_GOOGLE_SDK_ENUM = {
    "bus": TransitPreferences.TransitTravelMode.BUS,
    "subway": TransitPreferences.TransitTravelMode.SUBWAY,
    "train": TransitPreferences.TransitTravelMode.TRAIN,
    "tram": TransitPreferences.TransitTravelMode.LIGHT_RAIL,
    "rail": TransitPreferences.TransitTravelMode.RAIL,
}

TRAVEL_MODE_DRIVING = "driving"
TRAVEL_MODE_WALKING = "walking"
TRAVEL_MODE_BICYCLING = "bicycling"
TRAVEL_MODE_TRANSIT = "transit"
TRAVEL_MODES = [
    TRAVEL_MODE_DRIVING,
    TRAVEL_MODE_WALKING,
    TRAVEL_MODE_BICYCLING,
    TRAVEL_MODE_TRANSIT,
]
TRAVEL_MODES_TO_GOOGLE_SDK_ENUM = {
    TRAVEL_MODE_DRIVING: RouteTravelMode.DRIVE,
    TRAVEL_MODE_WALKING: RouteTravelMode.WALK,
    TRAVEL_MODE_BICYCLING: RouteTravelMode.BICYCLE,
    TRAVEL_MODE_TRANSIT: RouteTravelMode.TRANSIT,
}

TRAFFIC_MODELS = ["best_guess", "pessimistic", "optimistic"]
TRAFFIC_MODELS_TO_GOOGLE_SDK_ENUM = {
    "best_guess": TrafficModel.BEST_GUESS,
    "pessimistic": TrafficModel.PESSIMISTIC,
    "optimistic": TrafficModel.OPTIMISTIC,
}

ICON_DRIVING = "mdi:car"
ICON_WALKING = "mdi:walk"
ICON_BICYCLING = "mdi:bike"
ICON_TRANSIT = "mdi:bus"

ICONS = {
    TRAVEL_MODE_DRIVING: ICON_DRIVING,
    TRAVEL_MODE_WALKING: ICON_WALKING,
    TRAVEL_MODE_BICYCLING: ICON_BICYCLING,
    TRAVEL_MODE_TRANSIT: ICON_TRANSIT,
}

# googlemaps library uses "metric" or "imperial" terminology in distance_matrix
UNITS_METRIC = "metric"
UNITS_IMPERIAL = "imperial"
UNITS = [UNITS_METRIC, UNITS_IMPERIAL]
UNITS_TO_GOOGLE_SDK_ENUM = {
    UNITS_METRIC: Units.METRIC,
    UNITS_IMPERIAL: Units.IMPERIAL,
}

ATTR_DURATION: Final = "duration"
ATTR_DISTANCE: Final = "distance"
