import shutil
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

from src.backend.DeckManagement.DeckController import BackgroundImage, DeckController
from src.backend.PageManagement.Page import Page

# Import gtk modules
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

import sys
import os
import io
from loguru import logger as log
from PIL import Image, ImageEnhance, ImageOps
import math

import globals as gl

# Add plugin to sys.paths
sys.path.append(os.path.dirname(__file__))

from MediaController import MediaController
from MediaAction import MediaAction


class Play(MediaAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_key_down(self):
        status = self.plugin_base.mc.status(self.get_player_name())
        if status is None or status[0] != "Playing":
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

        if self.show_title():
            size = 0.75
            valign = -1
        else:
            size = 1
            valign = 0

        icon_path = os.path.join(self.plugin_base.PATH, "assets", "play.png")
        
        if status == None:
            if self.current_status == None:
                self.current_status = "Playing"
            image = Image.open(icon_path)
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
                if isinstance(thumbnail[0], io.BytesIO):
                    pass
                elif not os.path.exists(thumbnail[0]):
                    return
                try:
                    thumbnail = Image.open(thumbnail[0])
                except:
                    return


        image = Image.open(icon_path)

        if status == "Playing":
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(0.6)
        
        image = self.generate_image(background=thumbnail, icon=image, size=size, valign=valign)

        self.set_media(image=image)


class Pause(MediaAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_key_down(self):
        status = self.plugin_base.mc.status(self.get_player_name())
        if status is None or status[0] == "Playing":
            self.plugin_base.mc.pause(self.get_player_name())

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

        if self.show_title():
            size = 0.75
            valign = -1
        else:
            size = 1
            valign = 0

        icon_path = os.path.join(self.plugin_base.PATH, "assets", "pause.png")
        
        if status == None:
            if self.current_status == None:
                self.current_status = "Playing"
            image = Image.open(icon_path)
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
                if isinstance(thumbnail[0], io.BytesIO):
                    pass
                elif not os.path.exists(thumbnail[0]):
                    return
                try:
                    thumbnail = Image.open(thumbnail[0])
                except:
                    return


        image = Image.open(icon_path)

        if status == "Paused":
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(0.6)
        
        image = self.generate_image(background=thumbnail, icon=image, size=size, valign=valign)

        self.set_media(image=image)


class PlayPause(MediaAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            "Stopped": os.path.join(self.plugin_base.PATH, "assets", "stop.png"), #play.png might make more sense
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
                if isinstance(thumbnail[0], io.BytesIO):
                    pass
                elif not os.path.exists(thumbnail[0]):
                    return
                try:
                    thumbnail = Image.open(thumbnail[0])
                except:
                    return


        image = Image.open(file.get(status, file["Stopped"]))
        
        image = self.generate_image(background=thumbnail, icon=image, size=size, valign=valign)

        self.set_media(image=image)

class Next(MediaAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        self.set_top_label(str(title), font_size=12)
        self.set_center_label(self.get_settings().get("seperator_text", "--"), font_size=12)
        self.set_bottom_label(str(artist), font_size=12)

        ## Thumbnail
        thumbnail = None
        if self.get_settings().setdefault("show_thumbnail", True):
            thumbnail = self.plugin_base.mc.thumbnail(self.get_player_name())
            if thumbnail == None:
                thumbnail = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
            elif isinstance(thumbnail, list):
                if thumbnail[0] == None:
                    return
                if isinstance(thumbnail[0], io.BytesIO):
                    pass
                elif not os.path.exists(thumbnail[0]):
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



class ThumbnailBackground(MediaAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title: str = None
        self.artist: str = None
        self.original_background_image = None  # Cache the original background

    def on_ready(self):
        self.title = None
        self.artist = None
        self.original_background_image = None

    def on_tick(self):
        self.update_image()

    def get_config_rows(self) -> "list[Adw.PreferencesRow]":
        # Get parent rows (player selector only, exclude label and thumbnail toggles)
        parent_rows = super().get_config_rows()
        # Keep only the player selector (first row)
        rows = [parent_rows[0]]
        
        # Add size mode selector
        self.size_mode_model = Gtk.StringList()
        self.size_mode_selector = Adw.ComboRow(
            model=self.size_mode_model,
            title=self.plugin_base.lm.get("actions.thumbnail-background.size-mode.label"),
            subtitle=self.plugin_base.lm.get("actions.thumbnail-background.size-mode.subtitle")
        )
        
        # Populate size options
        size_options = [
            ("1x1", "1x1"),
            ("2x2", "2x2"),
            ("3x3", "3x3"),
            ("4x4", "4x4"),
            ("stretch", self.plugin_base.lm.get("actions.thumbnail-background.size-mode.stretch")),
            ("fill", self.plugin_base.lm.get("actions.thumbnail-background.size-mode.fill"))
        ]
        
        self.size_mode_options = [opt[0] for opt in size_options]
        for _, label in size_options:
            self.size_mode_model.append(label)
        
        self.load_size_mode_default()
        self.size_mode_selector.connect("notify::selected", self.on_change_size_mode)
        
        rows.append(self.size_mode_selector)
        return rows
    
    def load_size_mode_default(self):
        settings = self.get_settings()
        if settings is None:
            return
        
        size_mode = settings.setdefault("size_mode", "stretch")
        
        # Select the appropriate mode
        try:
            index = self.size_mode_options.index(size_mode)
            self.size_mode_selector.set_selected(index)
        except ValueError:
            self.size_mode_selector.set_selected(4)  # Default to stretch
    
    def on_change_size_mode(self, combo, *args):
        settings = self.get_settings()
        selected_index = combo.get_selected()
        if selected_index < len(self.size_mode_options):
            settings["size_mode"] = self.size_mode_options[selected_index]
            self.set_settings(settings)
            self.update_image()

    def update_image(self):
        if not self.get_is_present():
            return
        
        settings = self.get_settings()
        if settings is None:
            return
        
        size_mode = settings.setdefault("size_mode", "stretch")
        
        ## Thumbnail
        thumbnail = self.plugin_base.mc.thumbnail(self.get_player_name())
        if isinstance(thumbnail, list):
            if thumbnail[0] is None:
                thumbnail = None
                self.clear()
                return
            try:
                thumbnail = Image.open(thumbnail[0])
            except:
                thumbnail = None
                
        if thumbnail is None:
            self.clear()
            return
        
        # Handle different size modes
        if size_mode == "stretch":
            # Stretch to fit entire deck, always starting at 0,0
            key_rows, key_cols = self.deck_controller.deck.key_layout()
            key_width, key_height = self.deck_controller.get_key_image_size()
            spacing_x, spacing_y = self.deck_controller.key_spacing
            
            full_width = key_width * key_cols + spacing_x * (key_cols - 1)
            full_height = key_height * key_rows + spacing_y * (key_rows - 1)
            
            # Resize thumbnail to exact deck dimensions
            stretched_thumbnail = thumbnail.resize((full_width, full_height), Image.LANCZOS)
            
            self.deck_controller.background.set_image(
            image=BackgroundImage(
                self.deck_controller,
                image=stretched_thumbnail,
            ),
            update=True
            )
        elif size_mode == "fill":
            # Scale to longest side, center on deck
            self.set_fill_screen_background(thumbnail)
        else:
            # Grid sizes (1x1, 2x2, 3x3, 4x4)
            self.set_grid_sized_background(thumbnail, size_mode)

    def set_fill_screen_background(self, thumbnail: Image.Image):
        """Scale thumbnail to fill the screen by its longest side, centered."""
        # Get full deck image size
        key_rows, key_cols = self.deck_controller.deck.key_layout()
        key_width, key_height = self.deck_controller.get_key_image_size()
        spacing_x, spacing_y = self.deck_controller.key_spacing
        
        full_width = key_width * key_cols + spacing_x * (key_cols - 1)
        full_height = key_height * key_rows + spacing_y * (key_rows - 1)
        
        # Calculate scaling to fill by longest side
        thumb_width, thumb_height = thumbnail.size
        scale = max(full_width / thumb_width, full_height / thumb_height)
        
        new_width = int(thumb_width * scale)
        new_height = int(thumb_height * scale)
        
        # Resize thumbnail
        resized_thumbnail = thumbnail.resize((new_width, new_height), Image.LANCZOS)
        
        # Create a canvas of the full deck size
        canvas = Image.new("RGBA", (full_width, full_height), (0, 0, 0, 255))
        
        # Center the thumbnail
        x_offset = (full_width - new_width) // 2
        y_offset = (full_height - new_height) // 2
        
        canvas.paste(resized_thumbnail, (x_offset, y_offset))
        
        self.deck_controller.background.set_image(
            image=BackgroundImage(
                self.deck_controller,
                image=canvas,
            ),
            update=True
        )

    def set_grid_sized_background(self, thumbnail: Image.Image, size_mode: str):
        """Place thumbnail at specific grid size overlaid on current background."""
        try:
            # Parse size (e.g., "2x2" -> 2)
            grid_size = int(size_mode[0])
        except:
            # Fallback to stretch if parsing fails
            self.deck_controller.background.set_image(
                image=BackgroundImage(
                    self.deck_controller,
                    image=thumbnail,
                ),
                update=True
            )
            return
        
        # Get deck layout
        key_rows, key_cols = self.deck_controller.deck.key_layout()
        key_width, key_height = self.deck_controller.get_key_image_size()
        spacing_x, spacing_y = self.deck_controller.key_spacing
        
        # Get action position
        coords = None
        if hasattr(self.input_ident, 'coords'):
            coords = self.input_ident.coords  # (x, y) or (col, row)
        
        if coords is None:
            # Fallback to stretch if we can't get position
            self.deck_controller.background.set_image(
                image=BackgroundImage(
                    self.deck_controller,
                    image=thumbnail,
                ),
                update=True
            )
            return
        
        col, row = coords
        
        # Calculate full deck size
        full_width = key_width * key_cols + spacing_x * (key_cols - 1)
        full_height = key_height * key_rows + spacing_y * (key_rows - 1)
        
        # Get the original page/deck background, not the one with previous thumbnails
        background_canvas = self.get_original_background(full_width, full_height)
        
        # Calculate thumbnail size and position
        thumb_width = key_width * grid_size + spacing_x * (grid_size - 1)
        thumb_height = key_height * grid_size + spacing_y * (grid_size - 1)
        
        # Resize thumbnail
        resized_thumbnail = thumbnail.resize((thumb_width, thumb_height), Image.LANCZOS)
        
        # Calculate position on deck (allow overflow)
        x_pos = col * (key_width + spacing_x)
        y_pos = row * (key_height + spacing_y)
        
        # Paste thumbnail on background
        background_canvas.paste(resized_thumbnail, (x_pos, y_pos))
        
        self.deck_controller.background.set_image(
            image=BackgroundImage(
                self.deck_controller,
                image=background_canvas,
            ),
            update=True
        )
    
    def get_original_background(self, full_width: int, full_height: int) -> Image.Image:
        """Get the original deck or page background without any thumbnail overlays."""
        # If we have a cached original background, always use it
        if self.original_background_image is not None:
            try:
                return self.original_background_image.copy()
            except:
                self.original_background_image = None
        
        # We don't have a cache yet, so we need to load the original background
        # Get background settings from deck and page
        deck_settings = self.deck_controller.get_deck_settings()
        deck_background_settings = deck_settings.get("background", {})
        page_background_settings = self.deck_controller.active_page.dict.get("settings", {}).get("background", {})
        
        # Determine which background to use (same logic as load_background in DeckController)
        if deck_background_settings.get("enable", False) and not page_background_settings.get("overwrite", False):
            config = deck_background_settings
        elif page_background_settings.get("overwrite", False) and page_background_settings.get("show", False):
            config = page_background_settings
        else:
            config = {}
        
        background_path = config.get("media-path")
        
        # Also check the old page.dict["background"] structure
        if not background_path:
            old_bg = self.deck_controller.active_page.dict.get("background", {})
            background_path = old_bg.get("path")
        
        # Load the original background image if it exists
        if background_path and os.path.isfile(background_path):
            try:
                # Check if it's a video (we'll just use black background for videos)
                if background_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.gif')):
                    result = Image.new("RGBA", (full_width, full_height), (0, 0, 0, 255))
                    self.original_background_image = result.copy()
                    return result
                
                # Load and resize the image to full deck size
                with Image.open(background_path) as bg_image:
                    # Use ImageOps.fit to preserve aspect ratio like BackgroundImage does
                    fitted_bg = ImageOps.fit(bg_image.copy(), (full_width, full_height), Image.LANCZOS)
                    # Convert to RGBA if needed
                    if fitted_bg.mode != "RGBA":
                        fitted_bg = fitted_bg.convert("RGBA")
                    # Cache it for next time
                    self.original_background_image = fitted_bg.copy()
                    return fitted_bg
            except Exception as e:
                log.warning(f"Failed to load original background from {background_path}: {e}")
        
        # Fallback to black background
        result = Image.new("RGBA", (full_width, full_height), (0, 0, 0, 255))
        self.original_background_image = result.copy()
        return result

    def clear(self):
        if not self.get_is_present():
            return
        self.original_background_image = None  # Clear cache
        self.deck_controller.background.set_image(
            image=None,
            update=True
        )

    def on_removed_from_cache(self):
        self.clear()

    def on_remove(self) -> None:
        self.clear()


class MediaPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.mc = MediaController()
        self.lm = self.locale_manager
        self.lm.set_to_os_default()

        shutil.rmtree(os.path.join(gl.DATA_PATH, "com_core447_MediaPlugin", "cache"), ignore_errors=True)

        self.play_holder = ActionHolder(
            plugin_base=self,
            action_base=Play,
            action_id_suffix="Play",
            action_name=self.lm.get("actions.play.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED
            }
        )
        self.add_action_holder(self.play_holder)

        self.pause_holder = ActionHolder(
            plugin_base=self,
            action_base=Pause,
            action_id_suffix="Pause",
            action_name=self.lm.get("actions.pause.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED
            }
        )
        self.add_action_holder(self.pause_holder)

        self.play_pause_holder = ActionHolder(
            plugin_base=self,
            action_base=PlayPause,
            action_id_suffix="PlayPause",
            action_name=self.lm.get("actions.play-pause.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED
            }
        )
        self.add_action_holder(self.play_pause_holder)

        self.next_holder = ActionHolder(
            plugin_base=self,
            action_base=Next,
            action_id_suffix="Next",
            action_name=self.lm.get("actions.next.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED
            }
        )
        self.add_action_holder(self.next_holder)

        self.previous_holder = ActionHolder(
            plugin_base=self,
            action_base=Previous,
            action_id_suffix="Previous",
            action_name=self.lm.get("actions.previous.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED
            }
        )
        self.add_action_holder(self.previous_holder)

        self.info_holder = ActionHolder(
            plugin_base=self,
            action_base=Info,
            action_id_suffix="Info",
            action_name=self.lm.get("actions.info.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )
        self.add_action_holder(self.info_holder)

        self.thumbnail_holder = ActionHolder(
            plugin_base=self,
            action_base=ThumbnailBackground,
            action_id_suffix="Thumbnail",
            action_name=self.lm.get("actions.thumbnail.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )
        self.add_action_holder(self.thumbnail_holder)

        self.register(
            plugin_name=self.lm.get("plugin.name"),
            github_repo="https://github.com/StreamController/MediaPlugin",
            plugin_version="1.0.0",
            app_version="1.0.0-alpha"
        )

        self.request_dbus_permission("org.mpris.MediaPlayer2.*")
