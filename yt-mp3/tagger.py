import re, stagger


class TagException(Exception):
    def __init__(self, message):
        self.message = message


class Tags:
    def __init__(self):
        self.album = ""
        self.artist = ""
        self.title = ""


def parse_tags(filename: str) -> Tags:
    filename_without_ending = filename[:filename.rfind(".")]

    match = re.search("#uploader#(.+)#title#(.+)#id#.+", filename_without_ending)

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
    def __init__(self, tagparser=parse_tags):
        self.parse_tags = tagparser

    def tag(self, full_file_path):
        filename = full_file_path[full_file_path.rindex("/") + 1:]

        tags = self.parse_tags(filename)

        audio_tags = stagger.read_tag(full_file_path)
        audio_tags.album = tags.album
        audio_tags.artist = tags.artist
        audio_tags.title = tags.title
        audio_tags.write()
