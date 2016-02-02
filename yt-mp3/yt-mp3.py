import sys, os, env, tagger, syncer, doctor, symlinker
from argparse import ArgumentParser

VERSION = "0.0.1"


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
    if not os.path.isdir(download_path):
        message = "Your provided path is no directory, you have to create it! (Path={0})".format(download_path)
        raise AttributeError(message)

    if not download_path.endswith("/"):
        download_path += "/"

    # Create logger and parser environment
    parser_env = env.ParserEnvironment(download_path)
    channels = parser_env.load_sync_descriptions()

    # Create instructions
    instructions = []
    if args.instruction_doctor:
        instructions.append(doctor.delete_orpahned_items)

    if args.instruction_download:
        instructions.append(syncer.sync_channels)

    if args.instruction_tag:
        instructions.append(tagger.tag_channels)

    if len(instructions) == 0:
        message = "You have provided no instruction to yt-mp3! Nothing will be executed!"
        parser_env.log.error(message)

    # Symlinking (always executed)
    instructions.append(symlinker.make_symlinks)

    # Execute instructions
    [instruction(parser_env) for instruction in instructions]


if __name__ == "__main__":
    main(sys.argv[1:])
