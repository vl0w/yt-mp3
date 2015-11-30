from downloader import ConvertToMp3Downloader
from synchronizer import DateRangeChannelSynchronizer
import datetime, sys, argparse

LIGHTFOX_CHANNEL = "UCr10DaQrUqcCud3tfAMr6Gg"


def main(argv):
    parser = argparse.ArgumentParser("Synchronize a YouTube channel")
    parser.add_argument("-c", "--channel",
                        dest="channel_id",
                        help="The ID of the channel",
                        required=True)
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

    args = parser.parse_args()

    # Inject API KEY
    import youtube
    youtube.DEVELOPER_KEY = args.api_key

    # From date
    if args.from_date_string is not None:
        from_date = datetime.datetime.strptime(args.from_date_string, "%d.%m.%Y").date()
    else:
        from_date = datetime.date(2005, 2, 15)


    def download_video(video_id):
        downloader = ConvertToMp3Downloader(video_id)

        if args.album is not None:
            downloader.set_album_title(args.album)

        downloader.download(args.path)

    syncer = DateRangeChannelSynchronizer(args.channel_id, args.path, from_date=from_date)
    syncer.start_synchronization(download_video)


if __name__ == "__main__":
    main(sys.argv[1:])
