import os
import subprocess
from asyncio import sleep

import simplematrixbotlib as clientlib
from pytube import YouTube

creds = clientlib.Creds("https://home.server", "@your_bot:home.server", "bot_pass")
client = clientlib.Bot(creds)
PREFIX = '!'

ytpath = "./youtube"
ffmpeg = "path/to/your/ffmpeg"
done = []

if not os.path.exists(ffmpeg):
    print("You have to install ffmpeg and change the ffmpeg path in order to run this bot")

listdir = os.listdir(ytpath)
if os.listdir(ytpath):
    for file in listdir:
        os.remove(f"{ytpath}/{file}")


def complete_func(stream, file_path):
    done.append(file_path)


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
                    if args[(i + 1)] == "144" or args[(i + 1)] == "144p":
                        res = 144
                    elif args[(i + 1)] == "360" or args[(i + 1)] == "360p":
                        res = 360
                    elif args[(i + 1)] == "480" or args[(i + 1)] == "480p":
                        res = 480
                    elif args[(i + 1)] == "720" or args[(i + 1)] == "720p":
                        res = 720
                    elif args[(i + 1)] == "1080" or args[(i + 1)] == "1080p":
                        res = 1080
                    else:
                        await client.api.send_text_message(room.room_id, f"{args[(i + 1)]} is not a valid option for {args[i]}. Use !Help for more info.")
                        return False, False

                else:
                    await client.api.send_text_message(room.room_id, f"{args[i]} is not an available arg. Use !Help for more info")
                    return False, False
        return file_type, res

    elif not args:
        return file_type, res


async def convert(room, files, type):
    if type == "audio":
        output = "output.mp3"
        subprocess.check_call(f'"{ffmpeg}" -i {ytpath}/{files[0]} {ytpath}/{output}', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif type == "video":
        output = "output.mp4"
        subprocess.check_call(f'"{ffmpeg}" -i {ytpath}/{files[0]} -i {ytpath}/{files[1]} -c:v copy -c:a aac {ytpath}/{output}', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        await client.api.send_text_message(room, "Internal error occured during file conversion")

    while not os.path.exists(f"{ytpath}/{output}"):
        await sleep(1)
        pass

    file = output
    files.append(file)
    return file


async def download(yt, room, file_type, res, ytpath):
    stream = []
    resstr = f"{res}p"

    if file_type == "video":
        await client.api.send_text_message(room.room_id, f'Downloading "{yt.title}" as a {file_type}')
        if res == 0:
            stream.append(yt.streams.filter(progressive=True, file_extension="mp4", type="video").get_highest_resolution())
        elif res <= 720:
            stream.append(yt.streams.filter(progressive=True, file_extension="mp4", type="video", res=resstr).first())
        elif res >= 1080:
            stream.append(yt.streams.filter(progressive=False, file_extension="mp4", type="video", res=resstr).first())
            stream.append(yt.streams.filter(type="audio").get_audio_only())
    elif file_type == "audio":
        await client.api.send_text_message(room.room_id, f'Downloading "{yt.title}" as {file_type}')
        stream.append(yt.streams.filter(type="audio").get_audio_only())

    files = []
    for i in stream:
        if i == None:
            await client.api.send_text_message(room.room_id, f'Downloading failed because the stream couldnt be found')
            return False
        else:
            f = i.download(ytpath)
            while f not in done:
                await sleep(1)
                pass

            os.rename(f, f"{ytpath}/{i.type}.mp4")
            filename = f"{i.type}.mp4"
            files.append(filename)

    print("Download finished")

    if len(files) == 2:
        try:
            file = await convert(room, files, file_type)
            print("Converting finished")
        except Exception:
            await client.api.send_text_message(room.room_id, "ffmpeg failed.")
            raise

    elif len(files) == 1:
        file = files[0]
        if file_type == "audio":
            file = await convert(room, files, file_type)
            print("Converting finished")
    else:
        await client.api.send_text_message(room.room_id, "File failed to downloaded.")

    return file


@client.listener.on_message_event
async def command(room, message):
    words = message.body.rsplit(" ")

    if message.sender != client.async_client.user and message.body.startswith(f"{PREFIX}download"):
        print("!download has been initialized")
        args = []

        for i in range(len(words) - 2):
            i += 1
            if words[i] != "":
                args.append(words[i])

        if words[(len(words) - 1)].startswith("https://") or words[(len(words) - 1)].startswith("http://"):
            url = words[(len(words) - 1)]
            try:
                yt = YouTube(url, on_complete_callback=complete_func)
            except:
                await client.api.send_text_message(room.room_id, "This is either not a valid youtube link or the bot has connection troubles")
                return False

            # Defaults
            file_type = "video"
            res = 0

            file_type, res = await argfetch(room, args, file_type, res)
            if not file_type and not res:
                return False

            file = await download(yt, room, file_type, res, ytpath)

            try:
                await client.api.send_video_message(room.room_id, f"{ytpath}/{file}")
                print("Upload finished")
            except:
                await client.api.send_text_message(room.room_id, "File failed to upload, please check the upload of your homeserver")
                raise

            listdir = os.listdir(ytpath)
            for file in listdir:
                os.remove(f"{ytpath}/{file}")

        else:
            await client.api.send_text_message(room.room_id, "Not a valid link. The link has to start with http:// or https://")
            return False

    if message.sender != client.async_client.user and message.body.startswith(f"{PREFIX}help"):
        print("!help has been initialized")
        if os.path.exists("./messages/helpmessage.txt"):
            with open("./messages/helpmessage.txt", "r") as f:
                helpmessage = f.read()
        else:
            quit("Internal Error")

        await client.api.send_markdown_message(room.room_id, helpmessage)

client.run()
