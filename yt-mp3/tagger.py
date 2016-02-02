import re, stagger, glob, sys, os


class TagException(Exception):
    def __init__(self, message):
        self.message = message


class Tags:
    def __init__(self):
        self.album = ""
        self.artist = ""
        self.title = ""


class TagArchive:
    def __init__(self, archive_path: str):
        self.archive_path = archive_path

    def add(self, tagged_file: str):
        with open(self.archive_path, "a+") as f:
            f.write(tagged_file + "\n")

    def is_tagged(self, file: str):
        return os.exists(self.archive_path) and file in open(self.archive_path, "r")

    def clear(self):
        os.remove(self.archive_path)


def tag_channels(env):
    log = env.log
    log.info("Starting Tagging")

    tagger = StaggerTagger()
    archive = TagArchive(env.tag_archive_file_path)

    for file_path in glob.iglob(env.download_path + "/**/*", recursive=True):
        if not os.isdir(file_path):
            if not file_path.endswith(".mp3"):
                if not file_path.endswith(".txt") and not file_path.endswith(".log"):
                    log.warning("[mp3-tagging] Detected invalid file {0}. Only mp3 allowed.".format(file_path))

            elif archive.is_tagged(file_path):
                log.debug("[mp3-tagging] File already tagged: {0}".format(file_path))

            else:
                try:
                    tagger.tag(file_path)
                    archive.add(file_path)
                    log.debug("[mp3-tagging] Tagged: {0}".format(file_path))
                except TagException as e:
                    message = "[mp3-tagging] TagException! Reason: {0}. (file={1})".format(file_path, e.message)
                    log.error(message)
                except:
                    message = "[mp3-tagging] Exception! Reason: {0}. (file={1})".format(file_path, sys.exc_info()[0])
                    log.error(message)


def parsetags(filename: str) -> Tags:
    match = re.search("#uploader#(.+)#title#(.+)#id#.+", filename)

    if match is None:
        raise TagException("Couldn't parse tags from file {0}".format(filename))

    uploader = match.group(1)
    videotitle = match.group(2)

    # Parse artist and song title
    if "-" in videotitle:
        artist = videotitle.split("-", 1)[0].strip()
        song = videotitle.split("-", 1)[1].strip()
    else:
        artist = "Unknown"
        song = videotitle

    tags = Tags()
    tags.album = uploader
    tags.artist = artist
    tags.title = song

    return tags


class StaggerTagger:
    def tag(self, full_file_path):
        filename = full_file_path[full_file_path.rindex("/") + 1:]

        tags = parsetags(filename)

        audio_tags = stagger.read_tag(full_file_path)
        audio_tags.album = tags.album
        audio_tags.artist = tags.artist
        audio_tags.title = tags.title
        audio_tags.write()
