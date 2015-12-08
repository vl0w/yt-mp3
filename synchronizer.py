import datetime
import os.path
import json as json
import gc
import traceback
from urllib3.exceptions import MaxRetryError
from downloader import DownloadException
from youtube import query_videos_of_day
from concurrent.futures import ThreadPoolExecutor
import threading
from killswitch import killswitch_detected, KILLSWITCH_DETECTED_MESSAGE



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

STATE_LOCK = threading.Lock()

def state_save_locked(state: SynchronizerState, path: str):
    STATE_LOCK.acquire()
    state.save(path)
    STATE_LOCK.release()

def state_add_video_locked(state: SynchronizerState, video_id: str):
    STATE_LOCK.acquire()
    state.synchronized_videos.append(video_id)
    STATE_LOCK.release()

def state_add_date_locked(state: SynchronizerState, date):
    STATE_LOCK.acquire()
    state.add_synced_date(date)
    STATE_LOCK.release()

class DateRangeChannelSynchronizer:
    def __init__(self, channel_id: str, path: str, log, from_date=datetime.date(2005, 2, 15),
                 to_date=datetime.date.today()):
        self.channel_id = channel_id
        self.path = path
        self.state_path = path + "state.json"
        self.state = SynchronizerState()
        self.from_date = from_date
        self.to_date = to_date
        self.log = log

    def start_synchronization(self, invoke_downloader):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        if os.path.isfile(self.state_path):
            self.state.load(self.state_path)

        futures = []

        with ThreadPoolExecutor(max_workers=1) as executor:

            def fetch_and_download(date):
                if not killswitch_detected(self.path) and not self.state.is_date_already_synced(date):
                    self.log("Date {0} not fetched yet, searching for videos and downloading...".format(date))
                    queried_video_ids = query_videos_of_day(self.channel_id, date)

                    try:
                        if not killswitch_detected(self.path):
                            try:
                                for queried_video_id in queried_video_ids:
                                    if queried_video_id not in self.state.synchronized_videos:
                                        invoke_downloader(queried_video_id)

                                        # Update state locked
                                        state_add_video_locked(self.state, queried_video_id)
                                        state_save_locked(self.state, self.state_path)

                                        self.log("Video {0} downloaded".format(queried_video_id))

                                # Date downloaded
                                state_add_date_locked(self.state, date)
                                state_save_locked(self.state, self.state_path)
                                self.log("Date {0} synchronized".format(date))
                            except MaxRetryError:
                                self.log("MaxRetryError while downloading {0}".format(queried_video_id))
                                traceback.print_exc()
                            finally:
                                state_save_locked(self.state, self.state_path)

                    except DownloadException as e:
                        self.log(e)
                    finally:
                        gc.collect()

            current_date = self.from_date
            while current_date < self.to_date:
                if killswitch_detected(self.path):
                    self.log(KILLSWITCH_DETECTED_MESSAGE)
                    break

                future = executor.submit(fetch_and_download, current_date)
                futures.append(future)
                current_date = current_date + datetime.timedelta(days=1)

            [f.result() for f in futures]
            if not killswitch_detected(self.path):
                self.log("Everything is synchronized")
            else:
                self.log("Synchronization aborted by Killswitch")
