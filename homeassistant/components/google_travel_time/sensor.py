"""Support for Google travel time sensors."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_MODE, CONF_NAME, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_DISTANCE,
    ATTR_DURATION,
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN,
    ICON_DRIVING,
    ICONS,
)
from .coordinator import GoogleTravelTimeCoordinator


def sensor_descriptions(travel_mode: str) -> tuple[SensorEntityDescription, ...]:
    """Construct SensorEntityDescriptions."""
    return (
        SensorEntityDescription(
            translation_key="duration",
            icon=ICONS.get(travel_mode, ICON_DRIVING),
            key=ATTR_DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.MINUTES,
        ),
        SensorEntityDescription(
            translation_key="distance",
            icon=ICONS.get(travel_mode, ICON_DRIVING),
            key=ATTR_DISTANCE,
        ),
    )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Google travel time sensor entry."""
    name = config_entry.data.get(CONF_NAME, DEFAULT_NAME)
    coordinator = config_entry.runtime_data

    sensors: list[GoogleTravelTimeSensor] = [
        GoogleTravelTimeSensor(config_entry, name, sensor_description, coordinator)
        for sensor_description in sensor_descriptions(config_entry.options[CONF_MODE])
    ]

    async_add_entities(sensors, False)


class GoogleTravelTimeSensor(
    CoordinatorEntity[GoogleTravelTimeCoordinator], SensorEntity
):
    """Representation of a Google travel time sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: ConfigEntry,
        name: str,
        sensor_description: SensorEntityDescription,
        coordinator: GoogleTravelTimeCoordinator,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = sensor_description
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_description.key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, config_entry.data[CONF_API_KEY])},
            name=name,
            manufacturer="Google Inc.",
        )
        self._config_entry = config_entry

    async def async_added_to_hass(self) -> None:
        """Handle when entity is added."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data is not None:
            if self.entity_description.key == ATTR_DURATION:
                self._attr_native_value = round(
                    self.coordinator.data.duration.seconds / 60
                )
            elif self.entity_description.key == ATTR_DISTANCE:
                self._attr_native_value = (
                    self.coordinator.data.localized_values.distance.text
                )
            self.async_write_ha_state()
