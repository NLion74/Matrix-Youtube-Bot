import os.path

import simplematrixbotlib as clientlib
from pytube import YouTube

creds = clientlib.Creds("https://your.home.server", "@bot:home.server", "bot_password")
client = clientlib.Bot(creds)
PREFIX = '!'

ytpath = "./youtube"


async def argfetch(room, args, file_type, res):
    if args:
        for i in range(len(args) - 1):
            if str(args[i]).startswith("-"):
                if args[i] == "-t" or args[i] == "--type":
                    if args[(i + 1)] == "audio":
                        file_type = "audio"
                    elif args[(i + 1)] == "video":
                        file_type = "video"
                    else:
                        await client.api.send_text_message(room.room_id, f"{args[(i + 1)]} is not a valid option for {args[i]}. Use !Help for more info.")
                        return False, False

                elif args[i] == "-r" or args[i] == "--resolution":
                    if args[(i + 1)] == "360" or args[(i + 1)] == "360p":
                        res = "360p"
                    elif args[(i + 1)] == "480" or args[(i + 1)] == "480p":
                        res = "480p"
                    elif args[(i + 1)] == "720" or args[(i + 1)] == "720p":
                        res = "720p"
                    elif args[(i + 1)] == "1080" or args[(i + 1)] == "1080p":
                        res = "1080p"
                    else:
                        await client.api.send_text_message(room.room_id, f"{args[(i + 1)]} is not a valid option for {args[i]}. Use !Help for more info.")
                        return False, False

                else:
                    await client.api.send_text_message(room.room_id, f"{args[i]} is not an available arg. Use !Help for more info")
                    return False, False

        return file_type, res

    elif not args:
        return file_type, res


@client.listener.on_message_event
async def downloader(room, message):
    words = message.body.rsplit(" ")

    if message.sender != client.async_client.user and message.body.startswith(f"{PREFIX}download"):
        print("!download has been executed")
        args = []

        for i in range(len(words) - 2):
            i += 1
            if words[i] != "":
                args.append(words[i])

        if words[(len(words) - 1)].startswith("https://") or words[(len(words) - 1)].startswith("http://"):
            url = words[(len(words) - 1)]
            yt = YouTube(url)

            # Defaults
            file_type = "video"
            res = "360p"

            file_type, res = await argfetch(room, args, file_type, res)
            if not file_type and not res:
                return False

            if file_type == "video":
                await client.api.send_text_message(room.room_id, "Downloading Video File")
                stream = yt.streams.filter().get_by_resolution(res)
            elif file_type == "audio":
                await client.api.send_text_message(room.room_id, "Downloading Audio File")
                stream = yt.streams.filter().get_audio_only()

            file = stream.download(ytpath)

            await client.api.send_video_message(room.room_id, file)
            os.remove(file)

        else:
            return

    if message.sender != client.async_client.user and message.body.startswith(f"{PREFIX}help"):
        print("!help has been executed")
        if os.path.exists("./messages/helpmessage.txt"):
            with open("./messages/helpmessage.txt", "r") as f:
                helpmessage = f.read()
        else:
            quit("Internal Error")

        await client.api.send_markdown_message(room.room_id, helpmessage)


client.run()