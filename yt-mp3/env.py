import time, os, yaml, glob, stagger, json, logging, sys


class Mp3Tags:
    def __init__(self, artist="", album="", title=""):
        self.artist = artist
        self.album = album
        self.title = title


class DownloadedMusicFile:
    def __init__(self, file_mp3: str, file_info: str, file_thumbnail: str):
        self.file_mp3 = file_mp3
        self.file_info = file_info
        self.file_thumbnail = file_thumbnail

    def get_video_id(self):
        return self.file_mp3[self.file_mp3.rfind("/") + 1:self.file_mp3.rfind(".mp3")]

    def read_tags(self) -> Mp3Tags:
        audio_tags = stagger.read_tag(self.file_mp3)
        return Mp3Tags(audio_tags.artist, audio_tags.album, audio_tags.title)

    def load_info_json(self):
        with open(self.file_info, "r") as f:
            return json.load(f)


class SyncDescription:
    def __init__(self, name, youtube_url, target_directory_name):
        self.name = name
        self.youtube_url = youtube_url
        self.target_directory_name = target_directory_name


class ParserEnvironment:
    def __init__(self, path: str):
        self.path_main = path
        self.path_store = path + ".store/"
        self.path_data = self.path_store + "data/"
        self.path_log = self.path_store + "log/"
        self.path_archives = self.path_store + "archives/"

        self.file_channels = self.path_main + "channels.yaml"
        self.file_tagarchive = self.path_archives + "tag-archive.txt"

        # Create paths
        if not os.path.exists(self.path_main):
            os.mkdir(self.path_main)

        if not os.path.exists(self.path_store):
            os.mkdir(self.path_store)

        if not os.path.exists(self.path_data):
            os.mkdir(self.path_data)

        if not os.path.exists(self.path_log):
            os.mkdir(self.path_log)

        if not os.path.exists(self.path_archives):
            os.mkdir(self.path_archives)

        # Init logger
        self.file_log = "{0}run-{1}.log".format(self.path_log, int(round(time.time() * 1000)))

        self.log = logging.getLogger("yt-mp3")
        self.log.setLevel(logging.DEBUG)

        fh = logging.FileHandler(filename=self.file_log)
        fh.setLevel(logging.DEBUG)

        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setLevel(logging.INFO)

        formatter = logging.Formatter(u"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)

        self.log.addHandler(fh)
        self.log.addHandler(sh)

    def load_sync_descriptions(self) -> [SyncDescription]:
        if not os.path.isfile(self.file_channels):
            message = "Whoops, '{0}' is missing. ".format(self.file_channels)
            raise AttributeError(message)

        descriptions = []
        with open(self.file_channels, 'r') as stream:
            data = yaml.load(stream)
            for record in data:
                name = list(record.keys())[0]
                youtube_url = record[name]["youtube-url"]
                target_directory = record[name]["target-directory-name"]
                channel = SyncDescription(name, youtube_url, target_directory)
                descriptions.append(channel)

        return descriptions

    def file_for_channel_archive(self, description: SyncDescription) -> str:
        return self.path_archives + "archive-" + description.name + ".txt"

    def path_for_channel_data(self, description: SyncDescription) -> str:
        return self.path_data + description.name + "/"

    def load_downloaded_music_files(self) -> [DownloadedMusicFile]:
        music_files = []

        for path in glob.iglob(self.path_data + "/**/*", recursive=True):
            if not os.path.isdir(path) and path.endswith("mp3"):
                music_files.append(
                    DownloadedMusicFile(path, path.replace("mp3", "info.json"), path.replace("mp3", "jpg")))

        return music_files

    def sync_description_for_video_id(self, music_file: DownloadedMusicFile) -> SyncDescription:
        """
        A MP3 file is being downloaded because there of a SyncDescription.
        This method get a downloaded music file and searches the SyncDescription which was "responsible"
        for the music file's download.
        :param id: The YouTube Video ID
        :return: The SyncDescription which cause the video to be downloaded
        """
        video_id = music_file.get_video_id()
        sync_descriptions = self.load_sync_descriptions()

        for description in sync_descriptions:
            file_channel_archive = self.file_for_channel_archive(description)
            with open(file_channel_archive, "r") as f:
                for line in f:
                    if video_id in line:
                        return description
        raise AttributeError("It is uncertain, where the video {0} came from".format(video_id))
