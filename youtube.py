from concurrent.futures import ThreadPoolExecutor

from apiclient.discovery import build
import datetime

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = "???"


def query_videos_of_channel_in_date_range(channel_id: str, from_date, to_date):
    futures = []
    current_date = from_date
    with ThreadPoolExecutor(max_workers=100) as executor:
        while current_date < to_date:
            future = executor.submit(query_videos_of_day, channel_id, current_date)
            futures.append(future)
            current_date = current_date + datetime.timedelta(days=1)

    all_videos=[]

    for future in futures:
        videos = future.result()
        [all_videos.append(v) for v in videos]

    return all_videos


def query_videos_of_day(channel_id: str, of_date: datetime.date):
    date_range = create_date_range(of_date)

    from_date = str(date_range[0]).replace(" ", "T") + "Z"
    to_date = str(date_range[1]).replace(" ", "T") + "Z"

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    search_response = youtube.search().list(
        channelId=channel_id,
        part="id",
        maxResults=50,
        order="date",
        publishedAfter=from_date,
        publishedBefore=to_date
    ).execute()

    videos = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s" % (search_result["id"]["videoId"]))

    return videos


def query_video_of_channel(channel_id: str, amount_of_results: int):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    search_response = youtube.search().list(
        channelId=channel_id,
        part="id",
        maxResults=amount_of_results,
        order="date"
    ).execute()

    videos = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s" % (search_result["id"]["videoId"]))

    return videos


def create_date_range(date: datetime.date) -> datetime.datetime:
    from_date = datetime.datetime(date.year, date.month, date.day)
    tomorrow = date + datetime.timedelta(days=1)
    to_date = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day)
    return (from_date, to_date)
