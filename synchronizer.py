import datetime
import os.path
import json as json
import gc
from youtube import query_videos_of_day
from concurrent.futures import ThreadPoolExecutor
import threading
from killswitch import killswitch_detected, KILLSWITCH_DETECTED_MESSAGE

STATE_LOCK = threading.Lock()


class SynchronizerState:
    def __init__(self):
        self.synchronized_videos = []
        self.synchronized_dates = []

    def is_date_already_synced(self, date: datetime.date):
        date_as_string = datetime.datetime.strftime(date, "%d.%m.%Y")
        for date_string in self.synchronized_dates:
            if date_as_string == date_string:
                return True
        return False

    def add_synced_date(self, date: datetime.date):
        date_as_string = datetime.datetime.strftime(date, "%d.%m.%Y")
        self.synchronized_dates.append(date_as_string)

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

        if os.path.isfile(self.state_path):
            self.state.load(self.state_path)

        futures = []

        with ThreadPoolExecutor(max_workers=5) as executor:

            def fetch_and_download(date):
                if not killswitch_detected(self.path) and not self.state.is_date_already_synced(date):
                    print("Date {0} not fetched yet, searching for videos and downloading...".format(date))
                    queried_video_ids = query_videos_of_day(self.channel_id, date)

                    if not killswitch_detected(self.path):
                        for queried_video_id in queried_video_ids:
                            if queried_video_id not in self.state.synchronized_videos:
                                invoke_downloader(queried_video_id)

                                # Update state locked
                                STATE_LOCK.acquire()
                                self.state.synchronized_videos.append(queried_video_id)
                                STATE_LOCK.release()

                                print("Video {0} downloaded".format(queried_video_id))
                                gc.collect()

                        # Update & save state locked
                        STATE_LOCK.acquire()
                        self.state.add_synced_date(date)
                        self.state.save(self.state_path)
                        STATE_LOCK.release()

                        print("Date {0} synchronized".format(date))

            current_date = self.from_date
            while current_date < self.to_date:
                if killswitch_detected(self.path):
                    print(KILLSWITCH_DETECTED_MESSAGE)
                    break

                future = executor.submit(fetch_and_download, current_date)
                futures.append(future)
                current_date = current_date + datetime.timedelta(days=1)

        [f.result() for f in futures]
        if not killswitch_detected(self.path):
            print("Everything is synchronized")
        else:
            print("Synchronization aborted by Killswitch")
