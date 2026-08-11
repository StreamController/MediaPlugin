from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PageManagement.Page import Page

# Import gtk modules
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib
import globals as gl

from PIL import Image, ImageEnhance
import os
import math

class MediaAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.has_configuration = True

        self.current_status = None
        
    def on_key_down(self):
        pass

    def on_key_up(self):
        pass

    def on_tick(self):
        pass
    
    def get_config_rows(self) -> "list[Adw.PreferencesRow]":
        # Init ui elements
        self.player_model = Gtk.StringList()
        self.player_selector = Adw.ComboRow(model=self.player_model, title=self.plugin_base.lm.get("actions.media-action.bind-to-player.label"), subtitle=self.plugin_base.lm.get("actions.media-action.bind-to-player.subtitle"))
        self.player_selector.set_enable_search(True) #TODO: Implement


        self.label_toggle = Adw.SwitchRow(title=self.plugin_base.lm.get("actions.media-action.show-name-switch.label"), subtitle=self.plugin_base.lm.get("actions.media-action.show-name-switch.subtitle"))
        self.thumbnail_toggle = Adw.SwitchRow(title=self.plugin_base.lm.get("actions.media-action.show-thumbnail-switch.label"), subtitle=self.plugin_base.lm.get("actions.media-action.show-thumbnail-switch.subtitle"))

        self.idle_icon_row = Adw.ActionRow(
            title=self.plugin_base.lm.get("actions.media-action.idle-icon.label"),
        )
        self.choose_idle_icon_button = Gtk.Button.new_from_icon_name("document-open-symbolic")
        self.choose_idle_icon_button.set_valign(Gtk.Align.CENTER)
        self.idle_icon_row.add_suffix(self.choose_idle_icon_button)

        self.clear_idle_icon_button = Gtk.Button.new_from_icon_name("edit-clear-symbolic")
        self.clear_idle_icon_button.set_valign(Gtk.Align.CENTER)
        self.idle_icon_row.add_suffix(self.clear_idle_icon_button)

        self.load_config_defaults()

        self.player_selector.connect("notify::selected-item", self.on_change_player)
        self.label_toggle.connect("notify::active", self.on_toggle_label)
        self.thumbnail_toggle.connect("notify::active", self.on_toggle_thumbnail)
        self.choose_idle_icon_button.connect("clicked", self.on_choose_idle_icon_clicked)
        self.clear_idle_icon_button.connect("clicked", self.on_clear_idle_icon)

        return [self.player_selector, self.label_toggle, self.thumbnail_toggle, self.idle_icon_row]

    ## Custom methods
    def load_config_defaults(self):
        settings = self.get_settings()
        if settings == None:
            return
        
        show_label = settings.setdefault("show_label", True)
        show_thumbnail = settings.setdefault("show_thumbnail", True)
        idle_icon = settings.setdefault("idle_icon", "")

        # Update ui
        self.label_toggle.set_active(show_label)
        self.thumbnail_toggle.set_active(show_thumbnail)
        self.update_idle_icon_ui(idle_icon)
        self.update_player_selector()
    
    def update_player_selector(self):
        # Clear the model
        for i in range(self.player_model.get_n_items()):
            self.player_model.remove(0)

        players = self.plugin_base.mc.get_player_names(remove_duplicates=True)

        self.player_model.append(self.plugin_base.lm.get("actions.media-action-bind-to-player.all-players"))

        for player in players:
            self.player_model.append(player)

        # Add from settings if not already in the model
        if self.get_player_name() is not None:
            if self.get_player_name() not in players:
                self.player_model.append(self.get_player_name())

        # Select from settings
        if self.get_player_name() is not None:
            position = 0
            for i in range(self.player_model.get_n_items()):
                item = self.player_model.get_item(i).get_string()
                n = self.get_player_name()
                if self.player_model.get_item(i).get_string() == self.get_player_name():
                    position = i
                    break
            self.player_selector.set_selected(position)
    
    def on_change_player(self, combo, *args):
        settings = self.get_settings()
        if combo.get_selected_item().get_string() == self.plugin_base.lm.get("actions.media-action-bind-to-player.all-players"):
            del settings["player_name"]
        else:
            settings["player_name"] = combo.get_selected_item().get_string()
        self.set_settings(settings)

    def get_player_name(self):
        settings = self.get_settings()
        if settings is not None:
            return settings.get("player_name")

    def show_title(self, reload_key = True) -> bool:
        if self.get_settings() == None:
            return False
        title = self.plugin_base.mc.title(self.get_player_name())
        if self.get_settings().setdefault("show_label", True) and title is not None:
            label = None
            if isinstance(title, list):
                if len(title) > 0:
                    label = title[0]
                    # margins = [5, 0, 5, 10]
            if isinstance(title, str):
                if len(title) > 0:
                    label = title
                    # margins = [5, 0, 5, 10]
            self.set_bottom_label(str(self.shorten_label(label, 10)), font_size=12, update=reload_key)
            return True
        else:
            self.set_bottom_label(None, update=reload_key)
            return False

    def shorten_label(self, label, length):
        if label is None:
            return
        if len(label) > length:
            return label[:length-2] + ".."
        return label
    
    def on_toggle_label(self, switch, *args):
        settings = self.get_settings()
        settings["show_label"] = switch.get_active()
        self.set_settings(settings)
        # Update image
        self.on_tick()

    def on_toggle_thumbnail(self, switch, *args):
        settings = self.get_settings()
        settings["show_thumbnail"] = switch.get_active()
        self.set_settings(settings)
        # Update image
        self.on_tick()

    def update_idle_icon_ui(self, path):
        if path and os.path.isfile(path):
            filename = os.path.basename(path)
            self.idle_icon_row.set_subtitle(filename)
            self.clear_idle_icon_button.set_sensitive(True)
        else:
            default_text = self.plugin_base.lm.get("actions.media-action.idle-icon.default-subtitle")
            self.idle_icon_row.set_subtitle("None" if default_text is None else default_text)
            self.clear_idle_icon_button.set_sensitive(False)

    def on_choose_idle_icon_clicked(self, button):
        settings = self.get_settings()
        current_val = settings.get("idle_icon", "") if settings else ""
        
        def on_select_callback(path):
            if not path:
                return
            settings = self.get_settings()
            if settings is not None:
                settings["idle_icon"] = path
                self.set_settings(settings)
                self.update_idle_icon_ui(path)
                self.on_tick()

        GLib.idle_add(gl.app.let_user_select_asset, current_val, on_select_callback)

    def on_clear_idle_icon(self, button):
        settings = self.get_settings()
        if settings is not None:
            settings["idle_icon"] = ""
            self.set_settings(settings)
            self.update_idle_icon_ui("")
            self.on_tick()

    def get_idle_icon(self) -> Image.Image | None:
        settings = self.get_settings()
        if settings is None:
            return None
        idle_icon_path = settings.get("idle_icon", "")
        if idle_icon_path and os.path.isfile(idle_icon_path):
            try:
                return Image.open(idle_icon_path)
            except Exception as e:
                pass
        return None

    def generate_image(self, icon:Image.Image = None, background:Image.Image=None, valign: float = 0, halign: float = 0, size: float = 1):
        if background is None:
            background = Image.new("RGBA", (self.deck_controller.deck.key_image_format()["size"]), (0, 0, 0, 0))
        else:
            background = background.resize(self.deck_controller.deck.key_image_format()["size"])
        
        if icon is not None:
            # Resize
            lenght = int(self.deck_controller.deck.key_image_format()["size"][0] * size)
            icon = icon.resize((lenght, lenght))

        left_margin = int((background.width - icon.width) * (halign + 1) / 2)
        top_margin = int((background.height - icon.height) * (valign + 1) / 2)

        background.paste(icon, (left_margin, top_margin), icon)

        return background