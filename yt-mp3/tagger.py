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
    trailed = filename[:filename.rfind("-")]

    splitted = trailed.split("-", maxsplit=2)

    tags = Tags()
    tags.album = splitted[0].strip()
    tags.artist = splitted[1].strip()
    tags.title = splitted[2].strip()

    return tags


class Eyed3Tagger:
    def __init__(self, tagparser = parse_tags):
        self.parse_tags = tagparser

    def tag(self, full_file_path):
        filename = full_file_path[full_file_path.rindex("/") + 1:]

        tags = self.parse_tags(filename)

        audio_tags = stagger.read_tag(full_file_path)
        audio_tags.album = tags.album
        audio_tags.artist = tags.artist
        audio_tags.title = tags.title
        audio_tags.write()
