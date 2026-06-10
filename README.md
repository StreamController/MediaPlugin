# MediaPlugin

This plugin controls your player using the
[MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/) interface.

It will let you play/pause the current playing item and start the previous/next
track using the [StreamController](https://github.com/StreamController/StreamController).

## Actions

- **Play** - Starts media playback if the player is not currently playing.
- **Pause** - Pauses media playback if the player is currently playing.
- **PlayPause** - Toggles between play and pause states based on the current
  playback status. If more than one item is playing, it will pause/play all
- **Next** - Skips to the next track in the media queue.
- **Previous** - Returns to the previous track in the media queue.
- **Info** - Displays the current media title and artist information with and
  optional separator.
- **ThumbnailBackground** - Sets the current media thumbnail as the deck
  background image.
