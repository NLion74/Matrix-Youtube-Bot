import simplematrixbotlib as clientlib
from pytube import YouTube

config = clientlib.Config()
config.emoji_verify = True
config.ignore_unverified_devices = True

creds = clientlib.Creds("https://mtx.nlion.nl", "@youtube-downloader:nlion.nl", "dN0H57Ua$t9^^jJ$")
client = clientlib.Bot(creds, config)
PREFIX = '!'

ytpath = "./youtube"
ext = "mp4"
res = "360p"


@client.listener.on_message_event
async def downloader(room, message):
    print(f"{room.user_name(message.sender)} | {message.body} ({message.server_timestamp})")
    words = message.body.rsplit(" ")

    if message.sender != client.async_client.user and message.body.startswith(f"{PREFIX}download"):

        if words[(len(words) - 1)].startswith("https://") or words[(len(words) - 1)].startswith("http://"):

            url = words[(len(words) - 1)]
            args = []

            for i in range(len(words) - 2):
                i += 1
                if words[i] != "":
                    args.append(words[i])

            yt = YouTube(url)
            await client.api.send_text_message(room.room_id, "Downloading Video")

            yt.streams.filter(file_extension=ext).get_by_resolution(res).download(ytpath)
            yt.title.title()

            await client.api.send_video_message(room.room_id, f"{ytpath}/{yt.title.title()}.mp4")

        else:
            return


client.run()