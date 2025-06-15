"""Support for Google travel time sensors."""

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_NAME, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DEFAULT_NAME, DOMAIN
from .coordinator import GoogleTravelTimeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Google travel time sensor entry."""
    name = config_entry.data.get(CONF_NAME, DEFAULT_NAME)
    coordinator = config_entry.runtime_data

    sensor = GoogleTravelTimeSensor(config_entry, name, coordinator)

    async_add_entities([sensor], False)


class GoogleTravelTimeSensor(
    CoordinatorEntity[GoogleTravelTimeCoordinator], SensorEntity
):
    """Representation of a Google travel time sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        config_entry: ConfigEntry,
        name: str,
        coordinator: GoogleTravelTimeCoordinator,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, config_entry.data[CONF_API_KEY])},
            name=DOMAIN,
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
            self._attr_native_value = round(self.coordinator.data.duration.seconds / 60)
            self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes."""
        if self.coordinator.data is None:
            return None

        result = self._config_entry.options.copy()
        result["duration_in_traffic"] = (
            self.coordinator.data.localized_values.duration.text
        )
        result["duration"] = self.coordinator.data.localized_values.static_duration.text
        result["distance"] = self.coordinator.data.localized_values.distance.text

        result["origin"] = self.coordinator.resolved_origin
        result["destination"] = self.coordinator.resolved_destination
        return result
