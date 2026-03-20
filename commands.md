# Discord Bot Commands Documentation

Here is a complete list of commands available for the laptop control bot, grouped by their category.

## Audio (`audio.py`)
- `!speak <message>`: Make the laptop speak a message aloud using Native TTS. (e.g., `!speak "Hello there!"`)

## System Control (`control.py`)
- `!open_chrome`: Open Google Chrome on the laptop.
- `!chrome_search <search terms>`: Open Chrome and search Google directly.
- `!open <app_name>`: Attempt to open an application by name (e.g., `!open notepad`, `!open calc`).
- `!lock`: Lock the computer workstation.
- `!shutdown`: Initiate a system shutdown (defaults to a 10s delay).
- `!vol_up [amount]`: Increase system volume by the specified amount (1-50, default 10).
- `!vol_down [amount]`: Decrease system volume by the specified amount (1-50, default 10).
- `!mute`: Toggle system audio mute/unmute.
- `!vol_set <level>`: Set system master volume to an exact percentage (0-100).

## File Management (`files.py`)
- `!download <path>`: Download a specific file from the laptop to Discord. Note that Discord enforces a strict 25 MB upload limit.

## Apple Music Control (`music.py`)
- `!play <song name>`: Remotely open Apple Music, search, and play the specified song using GUI automation.
- `!pause_music`: Pause or resume the current song in Apple Music.
- `!stop_music`: Stop the current song and rewind to the beginning.
- `!next_song`: Skip to the next track.
- `!prev_song`: Go back to the previous track.

## Screenshot (`screenshot.py`)
- `!screenshot`: Take a screenshot of the primary laptop display and upload it to the chat.

## Simulated Streaming (`stream.py`)
- `!stream_start`: Starts a simulated live stream (updates a single Discord message with a new screenshot every second).
- `!stream_stop`: Stops the ongoing simulated live stream.

## System Information (`systeminfo.py`)
- `!sysinfo`: Display core hardware utilization including OS details, CPU usage, Memory/RAM stats, and Disk storage.

## Webcam (`webcam.py`)
- `!webcam`: Capture a snapshot using the laptop's default webcam and upload it.
