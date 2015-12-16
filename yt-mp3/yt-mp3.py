import youtube_dl, sys, re, glob
from argparse import ArgumentParser
from os.path import isfile, isdir
from logger import Logger
from tagger import StaggerTagger, TagException

VERSION = "0.0.1"


class RecursiveFileLooper:
    def __init__(self, path):
        self.path = path

    def loop(self, callback, include_files=".*"):
        for filename in glob.iglob(self.path + "/**/*", recursive=True):
            if re.match(include_files, filename) and not isdir(filename):
                callback(filename)


class ParserEnvironment:
    BATCH_FILE_NAME = "channels.txt"
    ARCHIVE_FILE_NAME = "archive.txt"
    ERROR_LOG_FILE_NAME = "error.log"
    OUTPUT_TEMPLATE_PATTERN = "%(uploader)s/%(uploader)s-%(title)s-%(id)s.%(ext)s"

    def __init__(self, download_path):
        self.download_path = download_path
        self.batch_file_path = download_path + ParserEnvironment.BATCH_FILE_NAME
        self.archive_file_path = download_path + ParserEnvironment.ARCHIVE_FILE_NAME
        self.output_template_pattern = download_path + ParserEnvironment.OUTPUT_TEMPLATE_PATTERN
        self.error_log_file_path = download_path + ParserEnvironment.ERROR_LOG_FILE_NAME

    def read_channels(self) -> []:
        if not isfile(self.batch_file_path):
            message = "There exists no file called '{0}' in your path. ".format(self.batch_file_path)
            message += "Please create this file and add the videos and channels which you want do download."
            raise AttributeError(message)

        urls = []
        for line in open(self.batch_file_path, "r"):
            if not line.startswith("#"):
                urls.append(line)

        return urls

def create_options(logger: Logger, archive_path:str, output_template_pattern:str):
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


def main(argv):
    parser = ArgumentParser(description="SOL MP3 Downloader v{0}".format(VERSION))
    parser.add_argument("-p", "--path",
                        dest="path",
                        help="The path where everything must be synchronized to",
                        required=True)
    parser.add_argument("--skip-download",
                        dest="skip_download",
                        action="store_true",
                        help="Skip downloading and only set tags",
                        default=False)

    args = parser.parse_args()

    # Fetch download path
    download_path = args.path
    if not isdir(download_path):
        message = "Your provided path is no directory, you have to create it! (Path={0})".format(download_path)
        raise AttributeError(message)

    if not download_path.endswith("/"):
        download_path += "/"

    parser_env = ParserEnvironment(download_path)
    log = Logger(download_path, append_to_existing_logs=False)

    if not args.skip_download:
        urls = parser_env.read_channels()
        for url in urls:
            channel_identification = url[url.rfind("/")+1:].strip()
            archive_path = "{0}/archive-{1}.txt".format(download_path, channel_identification)
            options = create_options(log, archive_path, parser_env.output_template_pattern)

            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download(urls)

    # Tag them
    tagger = StaggerTagger()

    def tag_file(file_path: str):
        if not file_path.endswith(".mp3"):
            if not file_path.endswith(".txt") and not file_path.endswith(".log"):
                log.warn("[mp3-tagging] Detected invalid file {0}. Only mp3 allowed.".format(file_path))
        else:
            try:
                tagger.tag(file_path)
                log.debug("[mp3-tagging] Tagged: {0}".format(file_path))
            except TagException as e:
                # With custom message
                message = "[mp3-tagging] TagException! Reason: {0}. (file={1})".format(file_path, e.message)
                log.error(message)
            except:  # LOGGER
                message = "[mp3-tagging] Exception! Reason: {0}. (file={1})".format(file_path, sys.exc_info()[0])
                log.error(message)

    looper = RecursiveFileLooper(parser_env.download_path)
    looper.loop(tag_file)


if __name__ == "__main__":
    main(sys.argv[1:])
