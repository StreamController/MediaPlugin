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
from gi.repository import Gtk, Adw, GLib

import sys
import os
import io
from PIL import Image, ImageEnhance, ImageOps

import globals as gl

# Load our submodules
plugin_dir = os.path.dirname(__file__)
sys.path.insert(0, plugin_dir)

from settings import PluginSettings, KEY_LOG_LEVEL, DEFAULT_LOG_LEVEL, KEY_COMPOSITE_TIMEOUT, DEFAULT_COMPOSITE_TIMEOUT
from log_wrapper import log, set_log_level

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
    """
    Media action that renders one or more thumbnail images onto the deck background.

    This class coordinates multiple `ThumbnailBackground` actions on the same page to
    produce a single composited background image. It uses several class-level caches
    and flags to avoid redundant work and reduce flicker:

    * Action list cache: `_cached_actions` and `_cached_page_id` cache the set of
      thumbnail actions for the current page so that repeated lookups are avoided.
    * Background cache: `_original_background_image` and `_cached_background_path`
      store the unmodified background so it can be reused while layering thumbnails
      on top, instead of reloading or recomputing it for every instance.
    * Batched compositing: `_pending_composite`, `_composite_in_progress`, and
      `_idle_composite_id` implement a batched composite pattern where changes from
      multiple actions are coalesced and applied once via a GLib idle callback.

    Each instance tracks its own thumbnail path, size/placement mode, and last
    contribution to the composite (`rendered_thumbnail`, `is_dirty`, etc.) so that
    only changed thumbnails trigger a recomposite. The actual update of the deck
    background is thus performed once per batch rather than once per action.
    """
    
    # Class-level cache for action list optimization
    _cached_actions = None  # Cached list of all thumbnail actions
    _cached_page_id = None  # ID of page for which actions are cached
    
    # Class-level coordinator for batched updates
    _pending_composite = False  # Flag indicating composite is needed
    _composite_in_progress = False  # Prevent recursive compositing
    _idle_composite_id = None  # GLib idle callback ID for deferred execution
    
    # Class-level background cache (shared by all actions)
    _original_background_image = None  # Cached original background
    _cached_background_path = None  # Track which background is cached
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Optimization: Track state to detect changes
        self.last_thumbnail_path = None
        self.last_size_mode = None
        self.last_background_path = None
        self.last_coords = None  # Track position for grid modes
        
        # Track rendering state for multi-thumbnail coordination
        self.rendered_thumbnail = None  # Store our rendered thumbnail for compositing
        self.is_dirty = False  # Flag indicating this action needs recompositing

    def _get_all_thumbnail_actions(self):
        """Get all ThumbnailBackground actions on the current page, sorted by type and position."""
        if not hasattr(self, 'page') or self.page is None:
            return [self]
        
        # Use page object id as cache key
        current_page_id = id(self.page)
        
        # Return cached list if valid
        if (ThumbnailBackground._cached_actions is not None and 
            ThumbnailBackground._cached_page_id == current_page_id):
            return ThumbnailBackground._cached_actions
        
        # Cache miss - rebuild the list
        actions = []
        try:
            # Iterate through all action objects on the page
            for input_type in self.page.action_objects.values():
                for identifier in input_type.values():
                    for state in identifier.values():
                        for action in state.values():
                            if isinstance(action, ThumbnailBackground):
                                actions.append(action)
        except Exception as e:
            log.error(f"Failed to collect all thumbnail actions while iterating through page.action_objects hierarchy: {e}")
            return [self]
        
        # If no actions found, at least include self (shouldn't happen if self is properly in action_objects)
        if not actions:
            log.warning("ThumbnailBackground: No thumbnail actions found on page, falling back to [self]")
            return [self]
        
        # Sort by layering order: Fill -> Stretch -> Grid (top-left to bottom-right)
        def get_sort_key(action):
            settings = action.get_settings()
            size_mode = settings.get("size_mode", "stretch") if settings else "stretch"
            
            # Priority order: fill=0, stretch=1, grid modes=2
            if size_mode == "fill":
                priority = 0
            elif size_mode == "stretch":
                priority = 1
            else:  # Grid modes (1x1, 2x2, 3x3, 4x4)
                priority = 2
            
            # Within same priority, sort by position (row, col)
            if hasattr(action.input_ident, 'coords'):
                row, col = action.input_ident.coords
                return (priority, row, col)
            
            # Handle badly configured actions without coordinates
            return (priority, float("inf"), float("inf"))
        
        actions.sort(key=get_sort_key)
        
        # Cache the result
        ThumbnailBackground._cached_actions = actions
        ThumbnailBackground._cached_page_id = current_page_id
        
        return actions

    def _request_composite(self):
        """Request a composite operation. Will be batched with other requests."""
        coords = self.input_ident.coords if hasattr(self.input_ident, 'coords') else None # type: ignore[attr-defined]
        log.trace(f"ThumbnailBackground: _request_composite called by [{coords}] with is_dirty state: [{self.is_dirty}]")
        # Mark this action as dirty
        self.is_dirty = True
        
        # Set the pending flag
        ThumbnailBackground._pending_composite = True
        
        # Cancel any existing timeout and schedule a new one
        # Use a small delay to allow all actions in current tick cycle to update
        if ThumbnailBackground._idle_composite_id is not None:
            log.trace("ThumbnailBackground: _request_composite - cancelling existing timeout")
            try:
                GLib.source_remove(ThumbnailBackground._idle_composite_id)
            except (OSError, ValueError):
                pass  # Timeout may have already fired or invalid ID
        
        timeout = self.plugin_base.get_settings().get(KEY_COMPOSITE_TIMEOUT, DEFAULT_COMPOSITE_TIMEOUT)
        log.trace(f"ThumbnailBackground: _request_composite - scheduling {timeout}ms timeout")
        ThumbnailBackground._idle_composite_id = GLib.timeout_add(
            timeout,  # milliseconds
            self._execute_composite_callback
        )
    
    def _execute_composite_callback(self):
        """Callback for GLib.timeout that executes the composite."""
        log.trace("ThumbnailBackground: _execute_composite_callback - timeout fired")
        # Clear the idle callback ID
        ThumbnailBackground._idle_composite_id = None
        
        try:
            # Execute the composite
            self._execute_composite_if_needed()
        except Exception as e:
            # Ensure we always reset the in_progress flag even if something goes wrong
            ThumbnailBackground._composite_in_progress = False
            log.error(f"ThumbnailBackground: Exception in _execute_composite_callback: {e}", exc_info=True)
        
        # Return False to prevent this callback from being called again
        return False
    
    def _execute_composite_if_needed(self):
        """Execute composite if pending and not already in progress."""
        log.trace(f"ThumbnailBackground: _execute_composite_if_needed - pending={ThumbnailBackground._pending_composite}, in_progress={ThumbnailBackground._composite_in_progress}")
        # Check if composite is needed and not already running
        if not ThumbnailBackground._pending_composite:
            log.trace("ThumbnailBackground: _execute_composite_if_needed - not pending, returning")
            return
        
        if ThumbnailBackground._composite_in_progress:
            log.trace("ThumbnailBackground: _execute_composite_if_needed - already in progress, returning")
            return
        
        # Mark as in progress to prevent recursion
        ThumbnailBackground._composite_in_progress = True
        ThumbnailBackground._pending_composite = False
        
        try:
            # Get all thumbnail actions on the page
            all_actions = self._get_all_thumbnail_actions()
            
            # Check if there are any actions with rendered thumbnails
            actions_with_thumbnails = [a for a in all_actions if a.rendered_thumbnail is not None]
            dirty_actions = [action for action in all_actions if action.is_dirty]
            log.trace(f"ThumbnailBackground: _execute_composite_if_needed - {len(dirty_actions)} dirty actions, {len(actions_with_thumbnails)} with thumbnails, {len(all_actions)} total")
            
            # If no actions have thumbnails to display, reload the page to restore the original background
            if not actions_with_thumbnails:
                log.trace("ThumbnailBackground: _execute_composite_if_needed - no thumbnails to display, reloading page to restore background")
                # Clear dirty flags first
                for action in all_actions:
                    action.is_dirty = False
                # Trigger a page reload to restore the original background
                if hasattr(self, 'page') and self.page is not None:
                    self.page.reload_similar_pages(reload_self=True)
                return
            
            if dirty_actions:
                log.trace("ThumbnailBackground: _execute_composite_if_needed - calling _composite_all_thumbnails")
                composite = None
                try:
                    composite = self._composite_all_thumbnails()
                    
                    # Apply the composite to the deck background
                    log.trace("ThumbnailBackground: _execute_composite_if_needed - applying composite to deck background")
                    self.deck_controller.background.set_image(
                        image=BackgroundImage(self.deck_controller, image=composite), # type: ignore[attr-defined] 
                        update=True
                    )
                    log.trace("ThumbnailBackground: _execute_composite_if_needed - composite applied, clearing dirty flags")
                finally:
                    # Always close the composite image to prevent memory leaks
                    if composite is not None:
                        try:
                            composite.close()
                        except Exception as e:
                            log.error(f"Failed to close composite image: {e}")
                
                # Clear all dirty flags
                for action in all_actions:
                    action.is_dirty = False
            else:
                log.trace("ThumbnailBackground: _execute_composite_if_needed - no dirty actions, skipping")
        finally:
            ThumbnailBackground._composite_in_progress = False
            log.trace("ThumbnailBackground: _execute_composite_if_needed - complete")
    
    def _composite_all_thumbnails(self):
        """Composite all thumbnail actions onto the base background."""
        log.trace("ThumbnailBackground: _composite_all_thumbnails - starting")
        full_width, full_height, _, _, _, _ = self.get_deck_dimensions()
        
        # Start with the base background
        log.trace("ThumbnailBackground: _composite_all_thumbnails - getting original background")
        composite = self.get_original_background(full_width, full_height)
        
        try:
            # Layer each thumbnail action's rendered image
            all_actions = self._get_all_thumbnail_actions()
            actions_with_thumbnails = [a for a in all_actions if a.rendered_thumbnail is not None]
            log.trace(f"ThumbnailBackground: _composite_all_thumbnails - compositing {len(actions_with_thumbnails)} thumbnails")
            
            for action in all_actions:
                if action.rendered_thumbnail is not None:
                    try:
                        # Ensure the thumbnail is in RGBA mode and matches the composite size
                        thumb = action.rendered_thumbnail
                        if thumb.mode != "RGBA":
                            thumb = thumb.convert("RGBA")
                        if thumb.size != composite.size:
                            thumb = thumb.resize(composite.size, Image.Resampling.LANCZOS)

                        # Use alpha_composite for proper RGBA compositing
                        composite.alpha_composite(thumb, (0, 0))
                    except Exception as e:
                        log.error(f"Failed to composite thumbnail: {e}")
            
            log.trace("ThumbnailBackground: _composite_all_thumbnails - complete")
            return composite
        except Exception as e:
            # If something goes wrong, clean up and re-raise
            log.error(f"Unexpected error in _composite_all_thumbnails: {e}", exc_info=True)
            try:
                composite.close()
            except Exception:
                pass
            raise
    
    def _should_update(self) -> bool:
        """Check if update is needed based on state changes."""
        
        # Check if media is playing
        title = self.plugin_base.mc.title(self.get_player_name()) # type: ignore[attr-defined]
        artist = self.plugin_base.mc.artist(self.get_player_name()) # type: ignore[attr-defined]
        
        # If both title and artist are None, no media is playing
        if title is None and artist is None:
            # Check if we were previously showing a thumbnail
            if self.last_thumbnail_path is not None:
                return True
            return False

        # Get current settings
        settings = self.get_settings()
        if settings is None:
            log.trace("ThumbnailBackground: No settings available, skipping update check")
            return False
        
        # Compare size mode change
        size_mode = settings.get("size_mode", "stretch")
        if size_mode != self.last_size_mode:
            log.trace(f"ThumbnailBackground: Size mode changed from {self.last_size_mode} to {size_mode}")
            return True

        # Compare position
        current_coords = self.input_ident.coords if hasattr(self.input_ident, 'coords') else None # type: ignore[attr-defined]
        if current_coords != self.last_coords:
            log.trace(f"ThumbnailBackground: Position changed from {self.last_coords} to {current_coords}")
            return True

        # Compare thumbnail path
        thumbnail_path = self._get_thumbnail_path()
        if thumbnail_path != self.last_thumbnail_path:
            log.trace(f"ThumbnailBackground: Thumbnail path changed from {self.last_thumbnail_path} to {thumbnail_path}")
            return True
        
        # Compare background path
        current_bg_path = self.get_background_path()
        if current_bg_path != self.last_background_path:
            log.trace(f"ThumbnailBackground: Background path changed from {self.last_background_path} to {current_bg_path}")
            return True
        
        # No relevant changes detected
        return False

    def _get_thumbnail_path(self) -> str | None:
        """
        Extract the thumbnail file path from the media controller's thumbnail data.
        Returns None if no thumbnail is available or if the data format is unexpected.
        """
        try:
            thumbnail_data = self.plugin_base.mc.thumbnail(self.get_player_name()) # type: ignore[attr-defined]
            if isinstance(thumbnail_data, list) and thumbnail_data:
                first_item = thumbnail_data[0]
                # Validate that the first item is a non-empty string and a valid file
                if isinstance(first_item, str) and first_item and first_item.lower() != "none":
                    if os.path.isfile(first_item):
                        return first_item
                    else:
                        log.trace(f"ThumbnailBackground: Thumbnail path '{first_item}' is not a valid file")
        except Exception as e:
            log.error(f"Failed to extract thumbnail path: {e}")
        return None

    def on_ready(self):
        """
        Initialize optimization caches to track the current state.
        Enables avoiding triggering an update each tick.
        An initial update is performed to display the starting background
        based on the current media state.
        """
        # Invalidate action list cache when page loads
        ThumbnailBackground._cached_actions = None
        ThumbnailBackground._cached_page_id = None
        
        # Clean up old background cache before resetting
        if ThumbnailBackground._original_background_image is not None:
            try:
                ThumbnailBackground._original_background_image.close()
            except Exception as e:
                log.error(f"Failed to close cached background image: {e}")
        
        # Always reset cache references
        ThumbnailBackground._original_background_image = None
        ThumbnailBackground._cached_background_path = None
        
        try:
            self._initialize_caches()
            self.update_image()
        except Exception as e:
            log.error(f"Failed to initialize ThumbnailBackground: {e}", exc_info=True)
            # Set defaults to ensure action is in a safe state
            self.last_size_mode = "stretch"
            self.last_thumbnail_path = None
            self.last_background_path = ""
            self.last_coords = None

    def on_tick(self):
        # Optimization: Only update if something changed
        if self._should_update():
            self.update_image()
        
    def get_config_rows(self) -> "list[Adw.PreferencesRow]":
        # Call parent to initialize player_selector (we only want this row, not label/thumbnail toggles)
        try:
            super().get_config_rows()
        except Exception as e:
            log.error(f"Failed to initialize parent config rows: {e}")
        
        # Get player selector from parent initialization
        if not hasattr(self, "player_selector") or self.player_selector is None:
            log.warning("Player selector not initialized in config rows")
            rows = []
        else:
            rows = [self.player_selector]
        
        # Add size mode selector
        self.size_mode_model = Gtk.StringList()
        self.size_mode_selector = Adw.ComboRow(
            model=self.size_mode_model,
            title=self.plugin_base.lm.get("actions.thumbnail-background.size-mode.label"),  # type: ignore[attr-defined]
            subtitle=self.plugin_base.lm.get("actions.thumbnail-background.size-mode.subtitle")  # type: ignore[attr-defined]
        )
        
        # Populate size options
        size_options = [
            ("1x1", "1x1"),
            ("2x2", "2x2"),
            ("3x3", "3x3"),
            ("4x4", "4x4"),
            ("stretch", self.plugin_base.lm.get("actions.thumbnail-background.size-mode.stretch")),  # type: ignore[attr-defined]
            ("fill", self.plugin_base.lm.get("actions.thumbnail-background.size-mode.fill"))  # type: ignore[attr-defined]
        ]
        
        self.size_mode_options = [opt[0] for opt in size_options]
        for _, label in size_options:
            self.size_mode_model.append(label)
        
        self.load_size_mode_default()
        self.size_mode_selector.connect("notify::selected", self.on_change_size_mode)
        
        rows.append(self.size_mode_selector)  # type: ignore[arg-type]
        return rows
    
    def load_size_mode_default(self):
        """
        Load the default size mode setting and apply it to the size mode selector.
        Load from actions settings, load and store ``"fill"`` as the default,
        If an invalid option is stored, fall back to the index for ``"fill"``.
        """
        settings = self.get_settings()
        if settings is None:
            return
        
        size_mode = settings.setdefault("size_mode", "fill")
        
        # Select the appropriate mode
        try:
            selected_index = self.size_mode_options.index(size_mode)
        except ValueError:
            # Default to "fill" if the stored mode is invalid
            selected_index = self.size_mode_options.index("fill")
        
        self.size_mode_selector.set_selected(selected_index)
    
    def on_change_size_mode(self, combo, *args):
        """
        When the user selects a different size for the thumbnail display in the UI:
        trigger a background image refresh to apply the new sizing behavior.
        :param combo: The size mode selector widget (e.g. an Adw.ComboRow) that
            emitted the change notification.
        :param args: Additional signal parameters provided by the toolkit,
            which are currently ignored.
        """
        settings = self.get_settings()
        if settings is None or not hasattr(self, 'size_mode_options') or not self.size_mode_options:
            log.warning("ThumbnailBackground: Cannot change size mode - settings or size_mode_options unavailable")
            return
        
        selected_index = combo.get_selected()
        if selected_index < 0 or selected_index >= len(self.size_mode_options):
            log.warning(f"ThumbnailBackground: Invalid size mode selection index {selected_index}")
            return
        
        # Invalidate cache since size mode affects sort order (fill/stretch/grid)
        ThumbnailBackground._cached_actions = None
        ThumbnailBackground._cached_page_id = None
        
        settings["size_mode"] = self.size_mode_options[selected_index]
        self.set_settings(settings)
        self.update_image()

    def update_image(self):
        """
        Update the background image with a thumbnail based on current settings.
        Retrieves the thumbnail path, loads the image, and applies the appropriate
        sizing/positioning mode (stretch, fill, or grid-based).
        Restore the original background if the thumbnail cannot be loaded.
        """
        log.trace("ThumbnailBackground: update_image called")
        if not self.get_is_present():
            return
        
        settings = self.get_settings()
        if settings is None:
            return
        
        size_mode = settings.setdefault("size_mode", "fill")
        self.last_size_mode = size_mode
        
        # Get thumbnail path using helper method
        thumbnail_path = self._get_thumbnail_path()
        
        if thumbnail_path is None:
            self.last_thumbnail_path = None
            self.restore_original_background()
            return
        
        # Load thumbnail image
        try:
            thumbnail = Image.open(thumbnail_path)
        except (OSError, ValueError) as e:
            log.error(f"Failed to load thumbnail image from {thumbnail_path}: {e}")
            self.last_thumbnail_path = None
            self.restore_original_background()
            return
        
        # Track thumbnail path, background path, and position
        self.last_thumbnail_path = thumbnail_path
        self.last_background_path = self.get_background_path()
        if hasattr(self.input_ident, 'coords'):
            self.last_coords = self.input_ident.coords # type: ignore[attr-defined]
        else:
            self.last_coords = None
        
        # Handle different size modes
        if size_mode == "stretch":
            # Stretch to exact deck dimensions (may distort aspect ratio)
            log.trace("ThumbnailBackground: calling set_stretch_background")
            self.set_stretch_background(thumbnail)
        elif size_mode == "fill":
            log.trace("ThumbnailBackground: calling set_fill_screen_background")
            self.set_fill_screen_background(thumbnail)
        else:
            # Grid sizes (1x1, 2x2, 3x3, 4x4)
            log.trace(f"ThumbnailBackground: calling set_grid_sized_background with mode {size_mode}")
            self.set_grid_sized_background(thumbnail, size_mode)
        
        # Close the thumbnail image to prevent memory leaks
        thumbnail.close()

    def _close_rendered_thumbnail(self) -> None:
        """Close and clear the rendered thumbnail to prevent memory leaks."""
        if self.rendered_thumbnail is not None:
            try:
                self.rendered_thumbnail.close()
            except Exception:
                pass
            self.rendered_thumbnail = None
    
    def _initialize_caches(self) -> None:
        """Initialize tracking caches with current state."""
        settings = self.get_settings()
        self.last_size_mode = settings.get("size_mode", "fill") if settings else "fill"
        self.last_thumbnail_path = self._get_thumbnail_path()
        self.last_background_path = self.get_background_path()
        self.last_coords = self.input_ident.coords if hasattr(self.input_ident, 'coords') else None  # type: ignore[attr-defined]

    def get_deck_dimensions(self):
        """Helper to get full deck dimensions."""
        key_rows, key_cols = self.deck_controller.deck.key_layout()
        key_width, key_height = self.deck_controller.get_key_image_size()  # type: ignore
        spacing_x, spacing_y = self.deck_controller.key_spacing
        
        full_width = key_width * key_cols + spacing_x * (key_cols - 1)
        full_height = key_height * key_rows + spacing_y * (key_rows - 1)
        
        return full_width, full_height, key_width, key_height, spacing_x, spacing_y

    def set_stretch_background(self, thumbnail: Image.Image):
        """Scale the given thumbnail to exactly match the full deck dimensions and set it"""        
        full_width, full_height, _, _, _, _ = self.get_deck_dimensions()
        
        self._close_rendered_thumbnail()
        self.rendered_thumbnail = thumbnail.resize((full_width, full_height), Image.Resampling.LANCZOS)
        
        # Convert to RGBA to ensure it has alpha channel for compositing
        if self.rendered_thumbnail.mode != 'RGBA':
            new_img = self.rendered_thumbnail.convert('RGBA')
            self.rendered_thumbnail.close()
            self.rendered_thumbnail = new_img
        
        self._request_composite()

    def set_fill_screen_background(self, thumbnail: Image.Image):
        """Scale thumbnail to fill the screen by its longest side, centered."""
        full_width, full_height, _, _, _, _ = self.get_deck_dimensions()
        
        # Calculate scaling to fill by longest side
        thumb_width, thumb_height = thumbnail.size
        scale = max(full_width / thumb_width, full_height / thumb_height)
        
        new_width = int(thumb_width * scale)
        new_height = int(thumb_height * scale)
        
        # Resize and center thumbnail
        resized_thumbnail = thumbnail.resize((new_width, new_height), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (full_width, full_height), (0, 0, 0, 0))
        
        x_offset = (full_width - new_width) // 2
        y_offset = (full_height - new_height) // 2
        canvas.paste(resized_thumbnail, (x_offset, y_offset))
        
        self._close_rendered_thumbnail()
        self.rendered_thumbnail = canvas
        resized_thumbnail.close()
        
        self._request_composite()

    def set_grid_sized_background(self, thumbnail: Image.Image, size_mode: str):
        """Place thumbnail at specific grid size overlaid on current background."""
        # Parse grid size
        try:
            grid_size = int(size_mode[0])
        except Exception:
            # Fallback to stretch behavior if parsing fails
            self.set_stretch_background(thumbnail)
            return
        
        # Get action position
        if not hasattr(self.input_ident, 'coords'):
            # Fallback to stretch behavior if no coords available
            self.set_stretch_background(thumbnail)
            return
        
        col, row = self.input_ident.coords  # type: ignore[attr-defined]
        full_width, full_height, key_width, key_height, spacing_x, spacing_y = self.get_deck_dimensions()
        
        # Calculate thumbnail dimensions
        thumb_width = key_width * grid_size + spacing_x * (grid_size - 1)
        thumb_height = key_height * grid_size + spacing_y * (grid_size - 1)
        
        # Resize and position thumbnail on a transparent canvas
        resized_thumbnail = thumbnail.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (full_width, full_height), (0, 0, 0, 0))
        x_pos = col * (key_width + spacing_x)
        y_pos = row * (key_height + spacing_y)
        canvas.paste(resized_thumbnail, (x_pos, y_pos))
        
        self._close_rendered_thumbnail()
        self.rendered_thumbnail = canvas
        resized_thumbnail.close()
        
        self._request_composite()
    
    def get_original_background(self, full_width: int, full_height: int) -> Image.Image:
        """
        Get the original deck or page background without any thumbnail overlays.
        
        Returns a copy of the cached background image to allow safe compositing.
        Multiple thumbnails may layer onto the same base background, so each caller
        gets an independent copy to avoid cross-contamination between composites.
        
        Returns a black canvas if no background is configured or if loading fails.
        """
        background_path = self.get_background_path()
        
        def _reset_background_cache():
            """Close and clear the cached background image."""
            if ThumbnailBackground._original_background_image is not None:
                try:
                    ThumbnailBackground._original_background_image.close()
                except Exception as e:
                    log.error(f"Failed to close background image: {e}")
            ThumbnailBackground._original_background_image = None
            ThumbnailBackground._cached_background_path = None
        
        # If no background is configured, always return black (don't cache)
        if not background_path or not os.path.isfile(background_path):
            log.trace(f"ThumbnailBackground: No valid background configured (path={background_path})")
            _reset_background_cache()
            return Image.new("RGBA", (full_width, full_height), (0, 0, 0, 255))
        
        # Check if background path has changed - invalidate cache if so
        if background_path != ThumbnailBackground._cached_background_path:
            log.trace(f"ThumbnailBackground: Background path changed from {ThumbnailBackground._cached_background_path} to {background_path}")
            _reset_background_cache()
        
        # Check if current background is a video/animated image
        # PIL cannot render videos, so return black canvas instead
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.gif', '.gifv'}
        is_video = any(background_path.lower().endswith(ext) for ext in video_extensions)
        if is_video:
            log.trace(f"ThumbnailBackground: Background is video file (not supported by PIL): {background_path}")
            _reset_background_cache()
            return Image.new("RGBA", (full_width, full_height), (0, 0, 0, 255))
        
        # Return a copy of cached background if available
        if ThumbnailBackground._original_background_image is not None:
            log.trace(f"ThumbnailBackground: Using cached background from {background_path}")
            try:
                return ThumbnailBackground._original_background_image.copy()
            except Exception as e:
                log.error(f"Failed to copy cached background image: {e}")
                _reset_background_cache()
        
        # Cache miss - load and fit image to deck size
        log.trace(f"ThumbnailBackground: Loading background image from {background_path}")
        try:
            with Image.open(background_path) as bg_image:
                result = ImageOps.fit(bg_image.copy(), (full_width, full_height), Image.Resampling.LANCZOS)
                if result.mode != "RGBA":
                    result = result.convert("RGBA")
            
            # Cache the result with its path
            ThumbnailBackground._original_background_image = result
            ThumbnailBackground._cached_background_path = background_path
            log.trace(f"ThumbnailBackground: Cached background image from {background_path}")
            return ThumbnailBackground._original_background_image.copy()
        except Exception as e:
            log.warning(f"Failed to load background from {background_path}: {e}")
            _reset_background_cache()
            return Image.new("RGBA", (full_width, full_height), (0, 0, 0, 255))
    
    def get_background_path(self) -> str:
        """
        Get the configured background path from deck or page settings.
        Retrieve from Page, falling back to Deck if no page override is set.
        """
        deck_settings = self.deck_controller.get_deck_settings()
        deck_bg = deck_settings.get("background", {})
        page_bg = self.deck_controller.active_page.dict.get("background", {})
        
        # Priority order:
        # 1. Page override enabled
        #    - show enabled: use page background
        #    - show disabled: return none
        # 2. Page override disabled
        #    - show enabled: use deck background
        #    - show disabled: return none
        # 3. No background configured: return none

        # Check if page is overriding
        if page_bg.get("overwrite", False):
            # Page is overriding - check if show is enabled
            if page_bg.get("show", False):
                path = page_bg.get("path")
                if path:
                    return path
            # Page override with show disabled = use black
            return ""
        
        # Page not overriding - check deck background
        if deck_bg.get("enable", False):
            path = deck_bg.get("path")
            if path:
                return path
        
        return ""

    def restore_original_background(self, force: bool = False):
        """
        Restore the page/deck background when no media is available.
        
        Clears this action's rendered thumbnail and requests a batched composite
        to show the base background and any remaining thumbnails from other actions.
        
        :param force: If True, requests composite even if no thumbnail was displayed.
            Used during action removal to ensure background is properly updated.
        """
        if not self.get_is_present() and not force:
            return
        
        changed = False
        # Clear this action's rendered thumbnail
        if self.rendered_thumbnail is not None:
            try:
                self.rendered_thumbnail.close()
            except Exception as e:
                log.error(f"Failed to close rendered thumbnail: {e}")
            self.rendered_thumbnail = None
            changed = True
        
        # Update tracking variables for no-media state
        self.last_thumbnail_path = None
        self.last_background_path = self.get_background_path()
        
        # Request batched composite only if something changed or forced
        # This avoids unnecessary page reloads when no thumbnail was displayed
        if changed or force:
            log.trace(f"ThumbnailBackground: Requesting composite to restore background (changed={changed}, force={force})")
            self._request_composite()

    def clear(self):
        """
        Cleanup cached images and reset state when action is removed.
        - Invalidate class-level caches ( background image)
        - Close and clear this action's rendered thumbnail
        - Clear the key image on deck
        - Request final composite to show remaining actions/background
        """

        log.debug("ThumbnailBackground: clear called, cleaning up cached images")
        
        # Reset this instance's tracking variables
        self.last_thumbnail_path = None
        self.last_size_mode = None
        self.last_background_path = ""
        self.last_coords = None
        
        # Close and clear this action's rendered thumbnail
        if self.rendered_thumbnail is not None:
            try:
                self.rendered_thumbnail.close()
            except Exception as e:
                log.error(f"Failed to close rendered thumbnail during clear: {e}")
            self.rendered_thumbnail = None
        
        # Request batched composite to update background with remaining actions
        try:
            self._request_composite()
        except Exception as e:
            log.error(f"Failed to request composite during clear: {e}")
        
        # Clear the key image so deck shows the composited background properly
        try:
            if self.get_is_present():
                self.set_media(image=None, update=True)
        except Exception:
            pass
            # Expected during removal when settings are already cleared
            pass
        
        # Clean up class-level background cache
        # Note: Don't invalidate cache for all instances - only clear if explicitly needed
        # The cache will be invalidated when background path changes or on page load
        if ThumbnailBackground._original_background_image is not None:
            try:
                ThumbnailBackground._original_background_image.close()
            except Exception as e:
                log.error(f"Failed to close cached background image during clear: {e}")
            ThumbnailBackground._original_background_image = None
        ThumbnailBackground._cached_background_path = None

    # Cleanup on removal from cache or deletion
    # These Three Methods are called in different removal scenarios.
    # Though I am not entirely sure when each is called, nor when it should be called.

    def on_removed_from_cache(self):
        """
        Seems to be called on remove via:
        Right Click -> Remove Action
        Select Action -> Delete Key
        """
        self.clear()

    def on_remove(self) -> None:
        """
        Seems to be called on remove via:
        Red Remove Action button in UI
        """       
        # Invalidate action list cache since we're removing an action
        ThumbnailBackground._cached_actions = None
        ThumbnailBackground._cached_page_id = None
        
        self.clear()
        # Reload the page to refresh the background with remaining actions
        if hasattr(self, 'page') and self.page is not None:
            self.page.reload_similar_pages(reload_self=True)

    def __del__(self):
        """
        * Sometimes * also called after on remove and in one case, only this was called??
        """
        self.clear()

class MediaPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.mc = MediaController()
        self.lm = self.locale_manager
        self.lm.set_to_os_default()
        
        # Initialize settings
        self._settings_manager = PluginSettings(self)
        self.has_plugin_settings = False
        
        # Initialize log level from settings
        settings = self.get_settings()
        log_level = settings.get(KEY_LOG_LEVEL, DEFAULT_LOG_LEVEL)
        set_log_level(log_level)

        shutil.rmtree(os.path.join(gl.DATA_PATH, "com_core447_MediaPlugin", "cache"), ignore_errors=True)

        self.play_holder = ActionHolder(
            plugin_base=self,
            action_base=Play, # type: ignore[arg-type]
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
            action_base=Pause,  # type: ignore[arg-type]
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
            action_base=PlayPause, # type: ignore[arg-type]
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
            action_base=Next,  # type: ignore[arg-type]
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
            action_base=Previous, # type: ignore[arg-type]
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
            action_base=Info, # type: ignore[arg-type]
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
            action_base=ThumbnailBackground, # type: ignore[arg-type]
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

    def get_settings_area(self):
        return self._settings_manager.get_settings_area()
