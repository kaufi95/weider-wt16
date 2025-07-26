"""The Weider WT16 Heat Pump integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_CREATE_DASHBOARD, DASHBOARD_VIEW_CONFIG
from .coordinator import WeiderWT16DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.CLIMATE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Weider WT16 from a config entry."""
    coordinator = WeiderWT16DataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Set up update listener for options
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Create dashboard if requested
    if entry.data.get(CONF_CREATE_DASHBOARD, False):
        await _create_dashboard(hass)

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options for the config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Update coordinator configuration
    await coordinator.async_update_config(entry)

    # Force a refresh with new settings
    await coordinator.async_request_refresh()


async def _create_dashboard(hass: HomeAssistant) -> None:
    """Automatically add the Weider WT16 view to the main dashboard."""
    try:
        lovelace = await _get_lovelace_system(hass)
        if not lovelace:
            return

        dashboard_config, dashboard_id, dashboards = await _get_dashboard_config(lovelace)
        if not dashboard_config:
            await _create_dashboard_file_fallback(hass)
            return

        await _add_view_to_dashboard(hass, dashboard_config, dashboard_id, dashboards)

    except Exception as err:
        _LOGGER.error("Failed to automatically add dashboard view: %s", err)
        await _create_dashboard_file_fallback(hass)


async def _get_lovelace_system(hass: HomeAssistant):
    """Get and validate the lovelace dashboard system."""
    from homeassistant.components.lovelace import dashboard

    lovelace = hass.data.get("lovelace")
    if not lovelace:
        _LOGGER.warning("Lovelace not found. Cannot automatically add view.")
        await _create_dashboard_file_fallback(hass)
        return None

    dashboard_mode = getattr(lovelace, "mode", "yaml")
    if dashboard_mode == "yaml":
        _LOGGER.warning("Dashboard is in YAML mode. Cannot automatically add view.")
        await _create_dashboard_file_fallback(hass)
        return None

    return lovelace


async def _get_dashboard_config(lovelace):
    """Get the dashboard configuration to modify."""
    dashboards = getattr(lovelace, "dashboards", {})
    dashboard_id = None
    dashboard_config = None

    # Try to find the overview dashboard
    for dash_id, dash_obj in dashboards.items():
        if dash_id == "overview" or getattr(dash_obj, "url_path", None) == "overview":
            dashboard_id = dash_id
            dashboard_config = await dash_obj.async_load(False)
            break

    # Fallback: try to get any dashboard
    if not dashboard_config:
        dashboard_items = list(dashboards.items())
        if dashboard_items:
            dashboard_id, dash_obj = dashboard_items[0]
            dashboard_config = await dash_obj.async_load(False)

    if not dashboard_config:
        _LOGGER.warning("No dashboard found to add view to.")

    return dashboard_config, dashboard_id, dashboards


async def _add_view_to_dashboard(hass: HomeAssistant, dashboard_config: dict, dashboard_id: str, dashboards: dict):
    """Add our view to the dashboard if it doesn't exist."""
    if "views" not in dashboard_config:
        dashboard_config["views"] = []

    # Check if our view already exists
    view_exists = any(view.get("path") == "warmepumpe" for view in dashboard_config["views"])

    if not view_exists:
        dashboard_config["views"].append(DASHBOARD_VIEW_CONFIG)

        # Save the updated dashboard
        dash_obj = dashboards[dashboard_id]
        await dash_obj.async_save(dashboard_config)

        _LOGGER.info("Successfully added 'Wärmepumpe' view to dashboard")

        # Create success notification
        await _create_success_notification(hass)
    else:
        _LOGGER.info("Wärmepumpe view already exists in dashboard")


async def _create_success_notification(hass: HomeAssistant):
    """Create a success notification for dashboard creation."""
    await hass.services.async_call(
        "persistent_notification",
        "create",
        {
            "title": "Weider WT16 Dashboard Added",
            "message": "The 'Wärmepumpe' tab has been automatically added to your dashboard!",
            "notification_id": "weider_wt16_success",
        },
    )


async def _create_dashboard_file_fallback(hass: HomeAssistant) -> None:
    """Fallback: Create dashboard file when automatic addition fails."""
    try:
        import os
        import yaml

        config_dir = hass.config.config_dir
        view_file = os.path.join(config_dir, "weider_wt16_view.yaml")

        with open(view_file, "w", encoding="utf-8") as file:
            yaml.dump(DASHBOARD_VIEW_CONFIG, file, default_flow_style=False, allow_unicode=True)

        await hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Weider WT16 Dashboard View Ready",
                "message": f"Could not automatically add view. Configuration saved to {view_file}. Add manually: Edit Dashboard → Add View → Show code editor → Copy content from the file.",
                "notification_id": "weider_wt16_manual",
            },
        )

    except Exception as err:
        _LOGGER.error("Failed to create fallback dashboard file: %s", err)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
