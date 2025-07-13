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

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Create dashboard if requested
    if entry.data.get(CONF_CREATE_DASHBOARD, False):
        await _create_dashboard(hass)

    return True


async def _create_dashboard(hass: HomeAssistant) -> None:
    """Automatically add the Weider WT16 view to the main dashboard."""
    try:
        from homeassistant.components.lovelace import dashboard
        
        # Try to access the lovelace dashboard system
        lovelace = hass.data.get("lovelace")
        if not lovelace:
            _LOGGER.warning("Lovelace not found. Cannot automatically add view.")
            await _create_dashboard_file_fallback(hass)
            return
        
        # Check if dashboard is in YAML mode
        dashboard_mode = getattr(lovelace, "mode", "yaml")
        if dashboard_mode == "yaml":
            # Dashboard is in YAML mode, can't modify programmatically
            _LOGGER.warning("Dashboard is in YAML mode. Cannot automatically add view.")
            await _create_dashboard_file_fallback(hass)
            return
            
        # Get the default dashboard config
        dashboard_id = None
        dashboard_config = None
        
        # Try to find the overview dashboard
        dashboards = getattr(lovelace, "dashboards", {})
        for dash_id, dash_obj in dashboards.items():
            if dash_id == "overview" or getattr(dash_obj, "url_path", None) == "overview":
                dashboard_id = dash_id
                dashboard_config = await dash_obj.async_load(False)
                break
        
        if not dashboard_config:
            # Fallback: try to get any dashboard
            dashboard_items = list(dashboards.items())
            if dashboard_items:
                dashboard_id, dash_obj = dashboard_items[0]
                dashboard_config = await dash_obj.async_load(False)
        
        if not dashboard_config:
            _LOGGER.warning("No dashboard found to add view to.")
            await _create_dashboard_file_fallback(hass)
            return
            
        # Add our view to the dashboard config
        if "views" not in dashboard_config:
            dashboard_config["views"] = []
            
        # Check if our view already exists
        view_exists = any(
            view.get("path") == "warmepumpe" 
            for view in dashboard_config["views"]
        )
        
        if not view_exists:
            dashboard_config["views"].append(DASHBOARD_VIEW_CONFIG)
            
            # Save the updated dashboard
            dash_obj = dashboards[dashboard_id]
            await dash_obj.async_save(dashboard_config)
            
            _LOGGER.info("Successfully added 'Wärmepumpe' view to dashboard")
            
            # Create success notification
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Weider WT16 Dashboard Added",
                    "message": "The 'Wärmepumpe' tab has been automatically added to your dashboard!",
                    "notification_id": "weider_wt16_success",
                },
            )
        else:
            _LOGGER.info("Wärmepumpe view already exists in dashboard")
            
    except Exception as err:
        _LOGGER.error("Failed to automatically add dashboard view: %s", err)
        await _create_dashboard_file_fallback(hass)


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