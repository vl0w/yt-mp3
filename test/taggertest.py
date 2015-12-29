from unittest import TestCase
from tagger import parsetags, TagException


class ParseTagsTest(TestCase):
    def test_no_uploader(self):
        self.assertRaises(TagException, parsetags, "#uploader##title#Bar.mp3")
        self.assertRaises(TagException, parsetags, "#title#Bar.mp3")

    def test_no_video_title(self):
        self.assertRaises(TagException, parsetags, "#uploader#Foo-title:.mp3")
        self.assertRaises(TagException, parsetags, "#uploader#Foo.mp3")

    def test_parse_album_from_uploader(self):
        tags = parsetags("#uploader#Lightfox 177#title#Winterlore - Ice of Old Night#id#FRf7PWDaipE.mp3")
        self.assertEqual("Lightfox 177", tags.album)

    def test_parse_artist(self):
        tags = parsetags("#uploader#Lightfox177#title#Winterlore - Ice of Old Night#id#FRf7PWDaipE.mp3")
        self.assertEqual("Winterlore", tags.artist)

    def test_parse_songtitle(self):
        tags = parsetags("#uploader#Lightfox177#title#Winterlore - Ice of Old Night#id#FRf7PWDaipE.mp3")
        self.assertEqual("Ice of Old Night", tags.title)

    def test_no_artist_and_songtitle_in_videotitle(self):
        tags = parsetags("#uploader#Lightfox177#title#My Top 100 Black Metal Albums of 2015#id#FRf7PWDaipE.mp3")
        self.assertEqual("Lightfox177", tags.album)
        self.assertEqual("Unknown", tags.artist)
        self.assertEqual("My Top 100 Black Metal Albums of 2015", tags.title)