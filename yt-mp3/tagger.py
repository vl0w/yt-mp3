import stagger, sys, os
from env import DownloadedMusicFile, Mp3Tags

class TagException(Exception):
    def __init__(self, message):
        self.message = message


class TagArchive:
    def __init__(self, archive_path: str):
        self.archive_path = archive_path
        self.archived = []
        self.__lazy_load_archive()

    def add(self, music_file: DownloadedMusicFile):
        with open(self.archive_path, "a+") as f:
            f.write(music_file.file_mp3 + "\n")

        self.archived.append(music_file.file_mp3)

    def is_already_tagged(self, file: DownloadedMusicFile):
        self.__lazy_load_archive()
        return file.file_mp3 in self.archived

    def clear(self):
        os.remove(self.archive_path)
        self.archived = []

    def __lazy_load_archive(self):
        if not self.archived and os.path.exists(self.archive_path):
            with open(self.archive_path, "r") as f:
                for line in f:
                    self.archived.append(line.replace("\n", ""))


def tag_channels(env):
    log = env.log
    log.info("Starting Tagging")

    tagger = StaggerTagWriter()
    archive = TagArchive(env.file_tagarchive)

    downloaded_music_files = env.load_downloaded_music_files()

    for music_file in downloaded_music_files:
        if archive.is_already_tagged(music_file):
            log.debug("File already tagged: {0}".format(music_file.file_mp3))
            continue

        try:
            tagger.tag(music_file)
            archive.add(music_file)
            log.debug("Tagged: {0}".format(music_file.file_mp3))
        except TagException as e:
            message = "TagException! Reason: {0}. (file={1})".format(music_file.file_mp3, e.message)
            log.error(message)
        except:
            message = "Exception! Reason: {0}. (file={1})".format(music_file.file_mp3, sys.exc_info()[0])
            log.error(message)


class StaggerTagWriter:
    def tag(self, music_file: DownloadedMusicFile):
        tags = self.__parse_tags(music_file)

        audio_tags = stagger.read_tag(music_file.file_mp3)
        audio_tags.album = tags.album
        audio_tags.artist = tags.artist
        audio_tags.title = tags.title
        audio_tags.picture = tags.file_thumbnail
        audio_tags.write()

    def __parse_tags(self, music_file: DownloadedMusicFile) -> Mp3Tags:
        data = music_file.load_info_json()

        tags = Mp3Tags
        tags.album = data["uploader"]
        tags.file_thumbnail = music_file.file_thumbnail

        videotitle = data["fulltitle"]
        if "-" in videotitle:
            tags.artist = videotitle.split("-", 1)[0].strip()
            tags.title= videotitle.split("-", 1)[1].strip()
        else:
            tags.artist = "Unknown"
            tags.title = videotitle

        return tags
