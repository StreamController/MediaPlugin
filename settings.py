from gi.repository import Gtk, Adw
import gi
import sys
import os

from loguru import logger as log

from src.backend.PluginManager import PluginBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

KEY_COMPOSITE_TIMEOUT = "composite_timeout"
DEFAULT_COMPOSITE_TIMEOUT = 80  # milliseconds

KEY_LOG_LEVEL = "log_level"
DEFAULT_LOG_LEVEL = "INFO"
AVAILABLE_LOG_LEVELS = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class PluginSettings:
    def __init__(self, plugin_base: PluginBase.PluginBase):
        self._plugin_base = plugin_base
        self._settings_cache = None

    def get_settings_area(self) -> Adw.PreferencesGroup:
        
        # Composite timeout spin button
        self._composite_timeout_adjustment = Gtk.Adjustment(
            value=DEFAULT_COMPOSITE_TIMEOUT,
            lower=10,
            upper=500,
            step_increment=10,
            page_increment=50
        )
        self._composite_timeout_spin = Adw.SpinRow(
            adjustment=self._composite_timeout_adjustment,
            title=self._plugin_base.lm.get("settings.composite-timeout.label"), # type: ignore
            subtitle=self._plugin_base.lm.get("settings.composite-timeout.subtitle")  # type: ignore
        )

        # Log level combo box
        self._log_level_model = Gtk.StringList()
        for level in AVAILABLE_LOG_LEVELS:
            self._log_level_model.append(level)
        
        self._log_level_combo = Adw.ComboRow(
            model=self._log_level_model,
            title=self._plugin_base.lm.get("settings.log-level.label"),  # type: ignore
            subtitle=self._plugin_base.lm.get("settings.log-level.subtitle")  # type: ignore
        )

        self._load_settings()
        self._composite_timeout_spin.connect("notify::value", self._on_change_composite_timeout)
        self._log_level_combo.connect("notify::selected", self._on_change_log_level)

        pref_group = Adw.PreferencesGroup()
        pref_group.set_title(self._plugin_base.lm.get("settings.title"))  # type: ignore
        pref_group.add(self._composite_timeout_spin)
        pref_group.add(self._log_level_combo)
        return pref_group

    def _get_cached_settings(self):
        """Get settings from cache or load from storage."""
        if self._settings_cache is None:
            self._settings_cache = self._plugin_base.get_settings()
        return self._settings_cache

    def _invalidate_cache(self):
        """Invalidate settings cache after modifications."""
        self._settings_cache = None

    def _load_settings(self):
        settings = self._get_cached_settings()
        composite_timeout = settings.get(KEY_COMPOSITE_TIMEOUT, DEFAULT_COMPOSITE_TIMEOUT)
        log_level = settings.get(KEY_LOG_LEVEL, DEFAULT_LOG_LEVEL)
        
        self._composite_timeout_spin.set_value(composite_timeout)
        
        try:
            selected_index = AVAILABLE_LOG_LEVELS.index(log_level)
        except ValueError:
            selected_index = AVAILABLE_LOG_LEVELS.index(DEFAULT_LOG_LEVEL)
        self._log_level_combo.set_selected(selected_index)

    def _update_settings(self, key: str, value: str):
        settings = self._get_cached_settings()
        settings[key] = value
        self._plugin_base.set_settings(settings)
        self._invalidate_cache()

    def _on_change_composite_timeout(self, spin, _):
        timeout = int(spin.get_value())
        self._update_settings(KEY_COMPOSITE_TIMEOUT, str(timeout))

    def _on_change_log_level(self, combo, _):
        selected_index = combo.get_selected()
        if 0 <= selected_index < len(AVAILABLE_LOG_LEVELS):
            level = AVAILABLE_LOG_LEVELS[selected_index]
            self._update_settings(KEY_LOG_LEVEL, level)
            # Apply the log level immediately
            self._apply_log_level(level)

    def _apply_log_level(self, level: str):
        """Apply the log level to the plugin logger."""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(__file__))
            from log_wrapper import set_log_level
            set_log_level(level)
        except Exception as e:
            log.error(f"Failed to set log level: {e}")

    def get_composite_timeout(self) -> int:
        """Get the configured composite timeout in milliseconds."""
        settings = self._get_cached_settings()
        return settings.get(KEY_COMPOSITE_TIMEOUT, DEFAULT_COMPOSITE_TIMEOUT)