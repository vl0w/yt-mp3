import os, datetime


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Logger:
    def __init__(self, root_path: str, append_to_existing_logs=True):
        self.path_debug = root_path + "debug.log"
        self.path_info = root_path + "info.log"
        self.path_warning = root_path + "warn.log"
        self.path_error = root_path + "error.log"

        if not append_to_existing_logs:
            self.clear_all_logs()

    def debug(self, message: str):
        self.log_to_console_and_file(message, self.path_debug)

    def info(self, message: str):
        self.log_to_console_and_file(message, self.path_error, color=Colors.OKBLUE)

    def warning(self, message: str):
        self.log_to_console_and_file(message, self.path_warning, color=Colors.WARNING)

    def error(self, message: str):
        self.log_to_console_and_file(message, self.path_error, color=Colors.FAIL)

    def log_to_console_and_file(self, message: str, log_path: str, color=None):
        time_wrapped_message = Logger.wraptime(message)

        if color is None:
            print(time_wrapped_message)
        else:
            Logger.print_with_color(time_wrapped_message, color)

        Logger.log_to_file(time_wrapped_message, log_path)

    @staticmethod
    def wraptime(message: str) -> str:
        return "{0} {1}".format(datetime.datetime.now(), message)

    def clear_all_logs(self):
        Logger.delete_file_if_exists(self.path_debug)
        Logger.delete_file_if_exists(self.path_info)
        Logger.delete_file_if_exists(self.path_warning)
        Logger.delete_file_if_exists(self.path_error)

    @staticmethod
    def print_with_color(message: str, color: Colors):
        print(color + message + Colors.ENDC)

    @staticmethod
    def log_to_file(message: str, file_path: str):
        with open(file_path, "a+") as file:
            file.write(message.encode("utf-8"))
            file.write("\n")

    @staticmethod
    def delete_file_if_exists(file_path: str):
        os.remove(file_path) if os.path.exists(file_path) else None
