import re, glob, sys
from argparse import ArgumentParser
from os.path import isfile, isdir
from logger import Logger
from tagger import tag_channels
from syncer import sync_channels

VERSION = "0.0.1"


class ParserEnvironment:
    BATCH_FILE_NAME = "channels.txt"
    ARCHIVE_FILE_NAME = "archive.txt"
    OUTPUT_TEMPLATE_PATTERN = "%(uploader)s/#uploader#%(uploader)s#title#%(title)s#id#%(id)s.%(ext)s"

    def __init__(self, download_path: str, log: Logger):
        self.log = log
        self.download_path = download_path
        self.batch_file_path = download_path + ParserEnvironment.BATCH_FILE_NAME
        self.archive_file_path = download_path + ParserEnvironment.ARCHIVE_FILE_NAME
        self.output_template_pattern = download_path + ParserEnvironment.OUTPUT_TEMPLATE_PATTERN

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


    args = parser.parse_args()

    # Download Path
    download_path = args.path
    if not isdir(download_path):
        message = "Your provided path is no directory, you have to create it! (Path={0})".format(download_path)
        raise AttributeError(message)

    if not download_path.endswith("/"):
        download_path += "/"

    # Create logger and parser environment
    log = Logger(download_path, append_to_existing_logs=False)
    parser_env = ParserEnvironment(download_path, log)

    # Create instructions
    instructions = []
    if args.instruction_download:
        instructions.append(sync_channels)

    if args.instruction_tag:
        instructions.append(tag_channels)

    if len(instructions) == 0:
        message = "You have provided no instruction to yt-mp3! Nothing will be executed!"
        log.error(message)
        #raise AttributeError(message)

    # Execute instructions
    [instruction(parser_env) for instruction in instructions]



if __name__ == "__main__":
    main(sys.argv[1:])
