import datetime, sys, argparse
from downloader import ConvertToMp3Downloader
from synchronizer import DateRangeChannelSynchronizer
from youtube import get_channel_id


def log(origin:str,message:str):
    print("Syncr({0}): {1}".format(origin, message))


def main(argv):
    parser = argparse.ArgumentParser("Synchronize a YouTube channel")
    parser.add_argument("-c", "--channel",
                        dest="channel_id",
                        help="The ID of the channel",
                        required=False)
    parser.add_argument("-u", "--user",
                        dest="user_name",
                        help="The user name",
                        required=False)
    parser.add_argument("-p", "--path",
                        dest="path",
                        help="The output path (folder) where everything should be synced to",
                        required=True)
    parser.add_argument("-k", "--api",
                        dest="api_key",
                        help="YouTube Data v3 API Key",
                        required=True)
    parser.add_argument("--from-date",
                        dest="from_date_string",
                        help="Sync starts from this date",
                        default=None,
                        required=False)
    parser.add_argument("--album",
                        dest="album",
                        help="Set album on downloaded MP3",
                        default=None,
                        required=False)
    parser.add_argument("--format",
                        dest="format",
                        help="Specifies the format the download. Either mp3 or mp4",
                        default="mp3",
                        required=False)

    args = parser.parse_args()

    # Inject API KEY
    import youtube
    youtube.DEVELOPER_KEY = args.api_key

    # From date
    if args.from_date_string is not None:
        from_date = datetime.datetime.strptime(args.from_date_string, "%d.%m.%Y").date()
    else:
        from_date = datetime.date(2005, 2, 15)

    # Parse by ID or channel name?
    channel_identification = None
    if hasattr(args,"channel_id") and args.channel_id is not None:
        channel_identification = args.channel_id
    elif hasattr(args,"user_name") and args.user_name is not None:
        fetched_channel_id = get_channel_id(args.user_name)
        if fetched_channel_id is None:
            log(args.user_name, "No channel found for username")
        channel_identification = fetched_channel_id

    if channel_identification is None:
        print("Either a user (-u) or channel (-c) must be provided!")
        return


    def download_as_mp3(video_id):
        downloader = ConvertToMp3Downloader(video_id)

        if args.album is not None:
            downloader.set_album_title(args.album)

        downloader.download_as_mp3(args.path)

    def download_as_mp4(video_id):
        downloader = ConvertToMp3Downloader(video_id)
        downloader.download_as_mp4(args.path)

    def log_synchronizer_messages(message:str):
        origin = "???"
        if args.user_name is not None:
            origin = args.user_name
        elif args.channel_id is not None:
            origin = args.channel_id
        log(origin, message)

    syncer = DateRangeChannelSynchronizer(channel_identification, args.path, log_synchronizer_messages, from_date=from_date)

    if args.format == "mp4":
        syncer.start_synchronization(download_as_mp4)
    elif args.format == "mp3":
        syncer.start_synchronization(download_as_mp3)
    else:
        print("Unknown format {0}".format(args.format))


if __name__ == "__main__":
    main(sys.argv[1:])