import youtube_dl
from logger import Logger


def sync_channels(env):
    env.log.info("Starting YouTube channel synchronization")

    urls = env.read_channels()
    for url in urls:
        channel_identification = url[url.rfind("/") + 1:].strip()
        archive_path = "{0}archive-{1}.txt".format(env, channel_identification)
        options = create_options(env.log, archive_path, env.output_template_pattern)

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([url])


def create_options(logger: Logger, archive_path: str, output_template_pattern: str):
    options = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],
        "download_archive": archive_path,
        "outtmpl": output_template_pattern,
        "ignoreerrors": True,
        "logger": logger
    }
    return options
