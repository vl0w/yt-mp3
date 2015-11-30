import datetime
import os.path
import json as json
from youtube import query_videos_of_channel_in_date_range
from concurrent.futures import ThreadPoolExecutor
import gc


class SynchronizerState:
    def __init__(self):
        self.synchronized_video_ids = []

    def save(self, path):
        data = json.dumps(self.__dict__)
        with open(path, "w") as file:
            file.write(data)

    def load(self, path):
        if os.path.exists(path):
            with open(path, "r") as file:
                json_data = json.loads(file.read())
                self.__dict__ = json_data


class DateRangeChannelSynchronizer:
    def __init__(self, channel_id: str, path: str, from_date=datetime.date(2005, 2, 15), to_date=datetime.date.today()):
        self.channel_id = channel_id
        self.path = path
        self.state_path = path + "state.json"
        self.state = SynchronizerState()
        self.from_date = from_date
        self.to_date = to_date

    def start_synchronization(self, invoke_downloader):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.state.load(self.state_path)

        print("Fetching videos from {0} to {1}".format(self.from_date, self.to_date))
        all_queried_video_ids = query_videos_of_channel_in_date_range(self.channel_id, self.from_date, self.to_date)
        video_ids_to_be_downloaded = list(all_queried_video_ids)
        for synchronized_video in self.state.synchronized_video_ids:
            if synchronized_video in video_ids_to_be_downloaded:
                video_ids_to_be_downloaded.remove(synchronized_video)
        print("{0} videos were found, {1} need to be downloaded".format(len(all_queried_video_ids),
                                                                        len(video_ids_to_be_downloaded)))

        futures = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            def download(video_id):
                invoke_downloader(video_id)
                self.state.synchronized_video_ids.append(video_id)
                self.state.save(self.state_path)
                print("Video {0} downloaded".format(video_id))
                gc.collect()

            for id in video_ids_to_be_downloaded:
                future = executor.submit(download, id)
                futures.append(future)

        [f.result() for f in futures]
