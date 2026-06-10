from functools import lru_cache
from itertools import groupby
import dbus
import sys
import os
import io
import base64
import globals as gl

from urllib.parse import urlparse
import requests

from loguru import logger as log

class MediaController:
    def __init__(self):
        self.session_bus = dbus.SessionBus()

        # Tracks the D-Bus bus names of players that were playing before a pause action.
        # When pause is pressed, all currently-playing sources are recorded here.
        # When play is pressed, only these remembered sources are resumed.
        self._previously_playing: set[str] = set()

        # Remembers the last player that was seen playing, so that when all
        # players are paused the UI doesn't jump back to an arbitrary player.
        self._last_active_player: str | None = None

        self.update_players()

    def update_players(self):
        mpris_players = []
        try:
            for i in self.session_bus.list_names():
                if str(i)[:22] == "org.mpris.MediaPlayer2":
                    mpris_players += [self.session_bus.get_object(i, '/org/mpris/MediaPlayer2')]
        except Exception as e:
            log.error("Could not connect to D-Bus session bus. Is the D-Bus daemon running?", e)
            return
        self.mpris_players = mpris_players

    def _get_bus_name(self, player) -> str:
        """Get the D-Bus bus name for a player proxy object."""
        return str(player.bus_name)

    def _get_playback_status(self, iface) -> str | None:
        """Get the playback status of a player interface."""
        try:
            properties = dbus.Interface(iface, 'org.freedesktop.DBus.Properties')
            return str(properties.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))
        except dbus.exceptions.DBusException as e:
            log.error(e)
            return None

    def get_player_names(self, remove_duplicates = False):
        names = []
        try:
            for player in self.mpris_players:
                properties = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
                name = properties.Get('org.mpris.MediaPlayer2', 'Identity')
                if remove_duplicates:
                    if name in names:
                        continue
                names.append(str(name))
        except Exception as e:
            log.error("Could not connect to D-Bus session bus. Is the D-Bus daemon running?", e)
        return names
    
    def get_active_player_name(self) -> str | None:
        """Return the Identity of the first currently-playing MPRIS player.
        Falls back to the last known active player if none are currently playing."""
        self.update_players()
        for player in self.mpris_players:
            try:
                properties = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
                status = str(properties.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))
                if status == "Playing":
                    name = str(properties.Get('org.mpris.MediaPlayer2', 'Identity'))
                    self._last_active_player = name
                    return name
            except dbus.exceptions.DBusException:
                pass
        return self._last_active_player

    def get_matching_ifaces(self, player_name: str = None) -> list[dbus.Interface]:
        self.update_players()
        """
        Retrieves a list of dbus interfaces that match the given player name.

        Args:
            player_name (str, optional): The name of the player to match. Defaults to None.
            If not provided, all interfaces will be returned.

        Returns:
            list[dbus.Interface]: A list of dbus interfaces that match the given player name.
        """
        ifaces = []
        for player in self.mpris_players:
            properties = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
            try:
                if player_name in [None, "", properties.Get('org.mpris.MediaPlayer2', 'Identity')]:
                    iface = dbus.Interface(player, 'org.mpris.MediaPlayer2.Player')
                    ifaces.append(iface)
            except dbus.exceptions.DBusException as e:
                if e.get_dbus_name() != "com.github.altdesktop.playerctld.NoActivePlayer":
                    log.warning(e)
        return ifaces

    def get_matching_players(self, player_name: str = None) -> list[tuple[str, dbus.Interface]]:
        """
        Like get_matching_ifaces, but returns (bus_name, iface) tuples
        so callers can identify individual player instances.
        """
        self.update_players()
        players = []
        for player in self.mpris_players:
            properties = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
            try:
                if player_name in [None, "", properties.Get('org.mpris.MediaPlayer2', 'Identity')]:
                    bus_name = self._get_bus_name(player)
                    iface = dbus.Interface(player, 'org.mpris.MediaPlayer2.Player')
                    players.append((bus_name, iface))
            except dbus.exceptions.DBusException as e:
                log.warning(e)
        return players
    
    def pause(self, player_name: str = None):
        """
        Pauses the media player specified by the `player_name` parameter.
        Before pausing, records which players are currently playing so they
        can be resumed later with play().

        Args:
            player_name (str, optional): The name of the media player to pause.
            If not provided, all media players will be paused.

        Returns:
            None
        """
        status = []
        players = self.get_matching_players(player_name)
        currently_playing = set()
        for bus_name, iface in players:
            try:
                playback_status = self._get_playback_status(iface)
                if playback_status == "Playing":
                    currently_playing.add(bus_name)
                iface.Pause()
                status.append(True)
            except dbus.exceptions.DBusException as e:
                log.error(e)
                status.append(False)

        # Only update the remembered set if at least one player was actually playing.
        # This avoids clearing the set if pause is pressed while already paused.
        if currently_playing:
            self._previously_playing = currently_playing

        return self.compress_list(status)

    def play(self, player_name: str = None):
        """
        Plays the media player specified by the `player_name` parameter.
        If there are remembered previously-playing sources (from a prior pause),
        only those sources will be resumed. Otherwise, all matching players
        will be played.

        Args:
            player_name (str, optional): The name of the media player to play.
            If not provided, all media players will be played.

        Returns:
            None
        """
        status = []
        players = self.get_matching_players(player_name)
        for bus_name, iface in players:
            try:
                if player_name is not None:
                    # Specific player requested: always play it
                    iface.Play()
                    status.append(True)
                elif self._previously_playing:
                    # General play with remembered set: only resume those
                    if bus_name in self._previously_playing:
                        iface.Play()
                        status.append(True)
                    else:
                        status.append(True)  # skip, not an error
                else:
                    iface.Play()
                    status.append(True)
            except dbus.exceptions.DBusException as e:
                log.error(e)
                status.append(False)

        # Clear the remembered set after resuming
        self._previously_playing.clear()

        return self.compress_list(status)
        
    def toggle(self, player_name: str = None):
        """
        Toggles the playback state of the media player specified by the `player_name` parameter.
        Uses the smart pause/play logic: when pausing, remembers which sources were playing;
        when playing, only resumes those remembered sources.

        Args:
            player_name (str, optional): The name of the media player to toggle.
            If not provided, all media players will be toggled.

        Returns:
            None
        """
        # Check if any matching player is currently playing
        players = self.get_matching_players(player_name)
        any_playing = False
        for bus_name, iface in players:
            playback_status = self._get_playback_status(iface)
            if playback_status == "Playing":
                any_playing = True
                break

        if any_playing:
            return self.pause(player_name)
        else:
            return self.play(player_name)
        
    def stop(self, player_name: str = None):
        """
        Stops the media player specified by the `player_name` parameter.

        Args:
            player_name (str, optional): The name of the media player to stop.
            If not provided, all media players will be stopped.

        Returns:
            None
        """
        status = []
        ifaces = self.get_matching_ifaces(player_name)
        for iface in ifaces:
            try:
                iface.Stop()
                status.append(True)
            except dbus.exceptions.DBusException as e:
                log.error(e)
                status.append(False)
        return self.compress_list(status)

    def next(self, player_name: str = None):
        """
        Plays the next track for the media player specified by the `player_name` parameter.
        If `player_name` is not provided, it will play the next track for all media players.

        Args:
            player_name (str, optional): The name of the media player. Defaults to None.

        Returns:
            None
        """
        status = []
        ifaces = self.get_matching_ifaces(player_name)
        for iface in ifaces:
            try:
                iface.Next()
                status.append(True)
            except dbus.exceptions.DBusException as e:
                log.error(e)
                status.append(False)

        return self.compress_list(status)

    def previous(self, player_name: str = None):
        """
        Plays the previous track for the media player specified by the `player_name` parameter.
        If `player_name` is not provided, it will play the previous track for all media players.

        Args:
            player_name (str, optional): The name of the media player. Defaults to None.

        Returns:
            None
        """
        status = []
        ifaces = self.get_matching_ifaces(player_name)
        for iface in ifaces:
            try:
                iface.Previous()
                status.append(True)
            except (KeyError, IndexError) as e:
                status.append(False)
            except dbus.exceptions.DBusException as e:
                log.error(e)
                status.append(False)

        return self.compress_list(status)

    def status(self, player_name: str = None) -> list[bool]:
        ifaces = self.get_matching_ifaces(player_name)
        status = []
        for iface in ifaces:
            try:
                properties = dbus.Interface(iface, 'org.freedesktop.DBus.Properties')
                status.append(str(properties.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')))
            except (KeyError, IndexError) as e:
                status.append(None)
            except dbus.exceptions.DBusException as e:
                log.error(e)
                status.append(None)

        return self.compress_list(status)
    
    def title(self, player_name: str = None) -> list[str]:
        ifaces = self.get_matching_ifaces(player_name)
        titles = []
        for iface in ifaces:
            try:
                properties = dbus.Interface(iface, 'org.freedesktop.DBus.Properties')
                metadata = properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                titles.append(str(metadata['xesam:title']))
            except (KeyError, IndexError) as e:
                titles.append(None)
            except dbus.exceptions.DBusException as e:
                log.error(e)
                titles.append(None)

        return self.compress_list(titles)
    
    def artist(self, player_name: str = None) -> list[str]:
        ifaces = self.get_matching_ifaces(player_name)
        titles = []
        for iface in ifaces:
            try:
                properties = dbus.Interface(iface, 'org.freedesktop.DBus.Properties')
                metadata = properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                titles.append(str(metadata['xesam:artist'][0]))
            except (KeyError, IndexError) as e:
                titles.append(None)
            except dbus.exceptions.DBusException as e:
                log.error(e)
                titles.append(None)

        return self.compress_list(titles)
    
    def thumbnail(self, player_name: str = None) -> list[str]:
        ifaces = self.get_matching_ifaces(player_name)
        thumbnails = []
        for iface in ifaces:
            try:
                properties = dbus.Interface(iface, 'org.freedesktop.DBus.Properties')
                metadata = properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                art_url = metadata.get('mpris:artUrl')
                if art_url is None:
                    thumbnails.append(None)
                    continue
                path = str(art_url)
                if not path:
                    thumbnails.append(None)
                    continue
                if path.startswith("data:"):
                    header, data = path.split(',', 1)
                    encoding = header.split(';')[1]
                    if encoding == "base64":
                        thumb = io.BytesIO(base64.b64decode(data))
                        thumbnails.append(thumb)
                        continue
                if path.startswith("https"):
                    path = self.get_web_thumnail(path)
                if not path:
                    thumbnails.append(None)
                    continue
                path = path.replace("file://", "")
                thumbnails.append(path)
            except (KeyError, IndexError) as e:
                thumbnails.append(None)
            except dbus.exceptions.DBusException as e:
                log.error(e)
                thumbnails.append(None)            

        return self.compress_list(thumbnails)

    def compress_list(self, _list) -> list | bool:
        if len(_list) == 0:
            return None
        
        def all_equal(iterable):
            if len(set(iterable)) == 0:
                return True
            
            first_element = iterable[0]
            first_element_occurrences = 0
            for element in iterable:
                if element == first_element:
                    first_element_occurrences += 1

            return first_element_occurrences == len(iterable)
        
        
        if all_equal(_list):
            return [_list[0]]
        
        return _list
    
    @lru_cache
    def get_web_thumnail(self, url: str) -> str:
        path = os.path.join(gl.DATA_PATH, "com_core447_MediaPlugin", "cache")
        # Download image
        return self.download_file(url, path)

    def get_file_name_from_url(self, url: str):
        """
        Extracts the file name from a given URL.

        Args:
            url (str): The URL from which to extract the file name.

        Returns:
            str: The file name extracted from the URL.
        """
        # Parse the url to extract the path
        parsed_url = urlparse(url)
        # Extract the file name from the path
        return os.path.basename(parsed_url.path)

    def download_file(self, url: str, path: str = "", file_name: str = None) -> str:
        """
        Downloads a file from the specified URL and saves it to the specified path.

        Args:
            url (str): The URL of the file to be downloaded.
            path (str): The path of the directory where the file will be saved. If a directory is provided, the filename will be extracted from the URL and appended to the path.

        Returns:
            path (str): The path of the downloaded file.
        """

        try:
            response = requests.get(url, stream=True)
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred during the request: {e}")
            return None

        if file_name is None:
            file_name = self.get_file_name_from_url(url)

        file_name = os.path.splitext(file_name)[0]
        _, extension = response.headers["content-type"].split("/")
        file_name += f".{extension}"

        path = os.path.join(path, file_name)

        if os.path.dirname(path) != "":
            os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as f:
            f.write(response.content)

        return path
