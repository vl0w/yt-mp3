from unittest import TestCase
from tagger import parse_tags


class ParseTagsTest(TestCase):
    def test_parse_album(self):
        tags = parse_tags("Lightfox177-Winterlore - Ice of Old Night-FRf7PWDaipE.mp3")
        self.assertEqual("Lightfox177", tags.album)

    def test_parse_artist(self):
        tags = parse_tags("Lightfox177-Winterlore - Ice of Old Night-FRf7PWDaipE.mp3")
        self.assertEqual("Winterlore", tags.artist)

    def test_parse_title(self):
        tags = parse_tags("Lightfox177-Winterlore - Ice of Old Night-FRf7PWDaipE.mp3")
        self.assertEqual("Ice of Old Night", tags.title)

    def test_parse_title_with_brackets(self):
        tags = parse_tags("Lightfox177-Alene Misantropi - Confessions Of A Man In Fear (Part II)-S6TADCyVoFE.mp3")
        self.assertEqual("Confessions Of A Man In Fear (Part II)", tags.title)

    def test_parse_title_with_additional_separator(self):
        tags = parse_tags("Lightfox177-Wildernessking - With Arms Like Wands (2016 - New Track)-9aJuhfKW9qM.mp3")
        self.assertEqual("With Arms Like Wands (2016 - New Track)", tags.title)