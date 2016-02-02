import sys, time
from argparse import ArgumentParser
from os.path import isfile, isdir
from logger import Logger
from tagger import tag_channels
from syncer import sync_channels
from doctor import delete_orpahned_items

VERSION = "0.0.1"


class Channel:
    def __init__(self, channel_url, download_folder_path):
        self.url = channel_url
        self.identification = channel_url[channel_url.rfind("/") + 1:].strip()
        self.archive_path = "{0}archive-{1}.txt".format(download_folder_path, self.identification)
        self.download_path = "{0}{1}/".format(download_folder_path, self.identification)

    def get_all_synchronized_video_ids(self) -> [str]:
        ids = []

        if isfile(self.archive_path):
            for line in open(self.archive_path, "r"):
                ids.append(line.split()[1])

        return ids


class ParserEnvironment:
    BATCH_FILE_NAME = "channels.txt"
    ARCHIVE_FILE_NAME = "archive.txt"
    TAG_ARCHIVE_FILE_NAME = "tag-archive.txt"
    OUTPUT_TEMPLATE_PATTERN = "%(uploader)s/#uploader#%(uploader)s#title#%(title)s#id#%(id)s.%(ext)s"

    def __init__(self, download_path: str, log: Logger):
        self.log = log
        self.download_path = download_path
        self.batch_file_path = download_path + ParserEnvironment.BATCH_FILE_NAME
        self.tag_archive_file_path = download_path + ParserEnvironment.TAG_ARCHIVE_FILE_NAME
        self.output_template_pattern = download_path + ParserEnvironment.OUTPUT_TEMPLATE_PATTERN

    def read_channels(self) -> [Channel]:
        if not isfile(self.batch_file_path):
            message = "There exists no file called '{0}' in your path. ".format(self.batch_file_path)
            message += "Please create this file and add the videos and channels which you want do download."
            raise AttributeError(message)

        channels = []
        for line in open(self.batch_file_path, "r"):
            if not line.startswith("#"):
                channel = Channel(line, self.download_path)
                channels.append(channel)

        return channels


def main(argv):
    parser = ArgumentParser(description="SOL MP3 Downloader v{0}".format(VERSION))
    parser.add_argument("-p", "--path",
                        dest="path",
                        help="The path where everything must be synchronized to",
                        required=True)
    parser.add_argument("-d", "--download",
                        dest="instruction_download",
                        action="store_true",
                        help="Downloads and synchronizes YouTube videos specified in the channels.txt file of the path",
                        default=False)
    parser.add_argument("-t", "--tag",
                        dest="instruction_tag",
                        action="store_true",
                        help="Fetches tags from downloaded videos and sets them in the ID3 area",
                        default=False)
    parser.add_argument("--doctor",
                        dest="instruction_doctor",
                        action="store_true",
                        help="Magically fixes and cleans your downloaded library.",
                        default=False)

    args = parser.parse_args()

    # Download Path
    download_path = args.path
    if not isdir(download_path):
        message = "Your provided path is no directory, you have to create it! (Path={0})".format(download_path)
        raise AttributeError(message)

    if not download_path.endswith("/"):
        download_path += "/"

    # Create logger and parser environment
    log_path = "{0}run-{1}.log".format(download_path, int(round(time.time() * 1000)))
    log = Logger(log_path, append_to_existing_logs=False)
    parser_env = ParserEnvironment(download_path, log)

    # Create instructions
    instructions = []
    if args.instruction_doctor:
        instructions.append(delete_orpahned_items)

    if args.instruction_download:
        instructions.append(sync_channels)

    if args.instruction_tag:
        instructions.append(tag_channels)

    if len(instructions) == 0:
        message = "You have provided no instruction to yt-mp3! Nothing will be executed!"
        log.error(message)
        # raise AttributeError(message)

    # Execute instructions
    [instruction(parser_env) for instruction in instructions]


if __name__ == "__main__":
    main(sys.argv[1:])
