import youtube_dl
from logger import Logger


def sync_channels(env):
    env.log.info("Starting YouTube channel synchronization")

    channels = env.read_channels()
    for channel in channels:
        options = create_options(env, channel)

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([channel.url])


def create_options(env, channel):
    options = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],
        "download_archive": channel.archive_path,
        "outtmpl": env.output_template_pattern,
        "ignoreerrors": True,
        "logger": env.log
    }
    return options
