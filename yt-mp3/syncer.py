import youtube_dl


def sync_channels(env):
    env.log.info("Starting YouTube channel synchronization")

    channels = env.load_sync_descriptions()
    for channel in channels:
        options = create_options(env, channel)

        with youtube_dl.YoutubeDL(options) as ydl:
            env.log.info("Synchronizing channel '{0}'".format(channel.name))
            ydl.download([channel.youtube_url])


def create_options(env, channel):
    return {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],
        "download_archive": env.file_for_channel_archive(channel),
        "outtmpl": env.path_for_channel_data(channel) + "%(id)s.%(ext)s",
        "ignoreerrors": True,
        "writeinfojson": True,
        "logger": env.log
    }
