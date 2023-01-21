# Matrix-Youtube-Bot
A simple Matrix Bot able to download videos and send them over Matrix

## Requirements

You will have to install simplematrixbotlib and pytube via pip. ffmpeg will also have to be installed.

## Preparation

To use the bot you will have to create a matrix account and then adjust the homeserver, username and password as well as the ffmpeg path in the matrix-bot.py. Afterwards you will be able to message the bot just like you would with any user. To use the bot see [Usage](https://github.com/NLion74/Matrix-Youtube-Bot#Usage)

## Usage

The bot can be used by following this format: ```!download [args] [url]```


### Commands:
```
!help                                   Used to show a help menu
                                        Format: !help

!download                               Command for downloading Youtube Videos.
                                        Format: !download [args] [url]
```

### Args:
```
!download -r, --resolution          [360p, 480p, 720p, 1080p]
!download -t, --type                [video, audio]
```
