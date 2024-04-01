from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.PluginBase import PluginBase

from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page

# Import gtk modules
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

import sys
import os
from loguru import logger as log
from PIL import Image, ImageEnhance
import math

# Add plugin to sys.paths
sys.path.append(os.path.dirname(__file__))

from MediaController import MediaController
from MediaAction import MediaAction

class PlayPause(MediaAction):
    def __init__(self, action_id: str, action_name: str,
                 deck_controller: "DeckController", page: Page, coords: str, plugin_base: PluginBase):
        super().__init__(action_id=action_id, action_name=action_name,
            deck_controller=deck_controller, page=page, coords=coords, plugin_base=plugin_base)

    def on_key_down(self):
        status = self.plugin_base.mc.status(self.get_player_name())
        if status is None:
            return
        status = status[0]
        if status == "Playing":
            self.plugin_base.mc.pause(self.get_player_name())
        else:
            self.plugin_base.mc.play(self.get_player_name())

    def on_key_up(self):
        pass

    def on_tick(self):
        self.update_image()

    def on_ready(self):
        self.update_image()

    def update_image(self):
        if self.get_settings() == None:
            # Page not yet fully loaded
            return
        status = self.plugin_base.mc.status(self.get_player_name())
        if isinstance(status, list):
            status = status[0]

        file = {
            "Playing": os.path.join(self.plugin_base.PATH, "assets", "pause.png"),
            "Paused": os.path.join(self.plugin_base.PATH, "assets", "play.png"),
        }
        
        if self.show_title():
            size = 0.75
            valign = -1
        else:
            size = 1
            valign = 0
        
        if status == None:
            if self.current_status == None:
                self.current_status = "Playing"
            file_path = file[self.current_status]
            image = Image.open(file_path)
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(0.6)
            self.set_media(image=image, size=size, valign=valign)
            return

        self.current_status = status

        ## Thumbnail
        thumbnail = None
        if self.get_settings().setdefault("show_thumbnail", True):
            thumbnail = self.plugin_base.mc.thumbnail(self.get_player_name())
            if thumbnail == None:
                thumbnail = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
            elif isinstance(thumbnail, list):
                if thumbnail[0] == None:
                    return
                if not os.path.exists(thumbnail[0]):
                    return
                try:
                    thumbnail = Image.open(thumbnail[0])
                except:
                    return


        image = Image.open(file[status])
        
        image = self.generate_image(background=thumbnail, icon=image, size=size, valign=valign)

        self.set_media(image=image)

class Next(MediaAction):
    def __init__(self, action_id: str, action_name: str,
                 deck_controller: "DeckController", page: Page, coords: str, plugin_base: PluginBase):
        super().__init__(action_id=action_id, action_name=action_name,
            deck_controller=deck_controller, page=page, coords=coords, plugin_base=plugin_base)

    def on_ready(self):
        self.update_image()

    def on_key_down(self):
        self.plugin_base.mc.next(self.get_player_name())

    def on_tick(self):
        self.update_image()

    def update_image(self):
        status = self.plugin_base.mc.status(self.get_player_name())
        if isinstance(status, list):
            status = status[0]

        if self.show_title():
            size = 0.75
            valign = -1
        else:
            size = 1
            valign = 0

        image = Image.open(os.path.join(self.plugin_base.PATH, "assets", "next.png"))
        if status == None:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(0.6)

        
        thumbnail = None
        if self.get_settings() is None:
            return
        if self.get_settings().setdefault("show_thumbnail", True):
            thumbnail = self.plugin_base.mc.thumbnail(self.get_player_name())
            if thumbnail == None:
                thumbnail = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
            elif isinstance(thumbnail, list):
                try:
                    thumbnail = Image.open(thumbnail[0])
                except:
                    return
                
        image = self.generate_image(background=thumbnail, icon=image, size=size, valign=valign)

        self.set_media(image=image)     

class Previous(MediaAction):
    def __init__(self, action_id: str, action_name: str,
                 deck_controller: "DeckController", page: Page, coords: str, plugin_base: PluginBase):
        super().__init__(action_id=action_id, action_name=action_name,
            deck_controller=deck_controller, page=page, coords=coords, plugin_base=plugin_base)

    def on_ready(self):
        self.update_image()

    def on_key_down(self):
        self.plugin_base.mc.previous(self.get_player_name())

    def on_tick(self):
        self.update_image()

    def update_image(self):
        status = self.plugin_base.mc.status(self.get_player_name())
        if isinstance(status, list):
            status = status[0]

        if self.show_title():
            size = 0.75
            valign = -1
        else:
            size = 1
            valign = 0

        image = Image.open(os.path.join(self.plugin_base.PATH, "assets", "previous.png"))
        if status == None:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(0.6)
        
        thumbnail = None
        if self.get_settings() is None:
            return
        if self.get_settings().setdefault("show_thumbnail", True):
            thumbnail = self.plugin_base.mc.thumbnail(self.get_player_name())
            if thumbnail == None:
                thumbnail = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
            elif isinstance(thumbnail, list):
                try:
                    thumbnail = Image.open(thumbnail[0])
                except:
                    return

        image = self.generate_image(background=thumbnail, icon=image, size=size, valign=valign)

        self.set_media(image=image) 

class Info(MediaAction):
    def __init__(self, action_id: str, action_name: str,
                 deck_controller: "DeckController", page: Page, coords: str, plugin_base: PluginBase):
        super().__init__(action_id=action_id, action_name=action_name,
            deck_controller=deck_controller, page=page, coords=coords, plugin_base=plugin_base)

    def on_tick(self):
        self.update_image()

    def update_image(self):
        title = self.plugin_base.mc.title(self.get_player_name())
        artist = self.plugin_base.mc.artist(self.get_player_name())

        if title is not None:
            title = self.shorten_label(title[0], 10)
        if title is not None:
            artist = self.shorten_label(artist[0], 10)

        if self.get_settings() is None:
            return

        self.set_top_label(title, font_size=12)
        self.set_center_label(self.get_settings().get("seperator_text", "--"), font_size=12)
        self.set_bottom_label(artist, font_size=12)

        thumbnail = None
        if self.get_settings().setdefault("show_thumbnail", True):
            thumbnail = self.plugin_base.mc.thumbnail(self.get_player_name())
            if isinstance(thumbnail, list):
                if thumbnail[0] == None:
                    return
                if not os.path.exists(thumbnail[0]):
                    return
                try:
                    thumbnail = Image.open(thumbnail[0])
                except:
                    return
                
        self.set_media(image=thumbnail)

    def get_config_rows(self):
        super_rows =  super().get_config_rows()
        super_rows.pop(1) # Remove label toggle row
        self.seperator_text_entry = Adw.EntryRow(title=self.plugin_base.lm.get("actions.info.seperator.text"))

        self.load_own_config_defaults()

        self.seperator_text_entry.connect("notify::text", self.on_change_seperator_text)

        return super_rows + [self.seperator_text_entry]
    
    def load_own_config_defaults(self):
        settings = self.get_settings()
        settings.setdefault("seperator_text", "--")
        self.set_settings(settings)

        # Update ui
        self.seperator_text_entry.set_text(settings["seperator_text"])

    def on_change_seperator_text(self, entry, *args):
        settings = self.get_settings()
        settings["seperator_text"] = entry.get_text()
        self.set_settings(settings)

        # Update image
        self.set_center_label(self.get_settings().get("seperator_text", "--"), font_size=12)

class MediaPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.mc = MediaController()
        self.lm = self.locale_manager
        self.lm.set_to_os_default()

        self.play_pause_holder = ActionHolder(
            plugin_base=self,
            action_base=PlayPause,
            action_id="com_core447_MediaPlugin::PlayPause",
            action_name=self.lm.get("actions.play-pause.name")
        )
        self.add_action_holder(self.play_pause_holder)

        self.next_holder = ActionHolder(
            plugin_base=self,
            action_base=Next,
            action_id="com_core447_MediaPlugin::Next",
            action_name=self.lm.get("actions.next.name")
        )
        self.add_action_holder(self.next_holder)

        self.previous_holder = ActionHolder(
            plugin_base=self,
            action_base=Previous,
            action_id="com_core447_MediaPlugin::Previous",
            action_name=self.lm.get("actions.previous.name")
        )
        self.add_action_holder(self.previous_holder)

        self.info_holder = ActionHolder(
            plugin_base=self,
            action_base=Info,
            action_id="com_core447_MediaPlugin::Info",
            action_name=self.lm.get("actions.info.name")
        )
        self.add_action_holder(self.info_holder)

        self.register(
            plugin_name=self.lm.get("plugin.name"),
            github_repo="https://github.com/StreamController/MediaPlugin",
            plugin_version="1.0.0",
            app_version="1.0.0-alpha"
        )

        self.request_dbus_permission("org.mpris.MediaPlayer2.*")