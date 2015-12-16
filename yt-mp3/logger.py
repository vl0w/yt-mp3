import os

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
    def __init__(self, root_path: str):
        self.path_debug = root_path + "debug.log"
        self.path_info = root_path + "info.log"
        self.path_warning = root_path + "warn.log"
        self.path_error = root_path + "error.log"

        Logger.delete_file_if_exists(self.path_debug)
        Logger.delete_file_if_exists(self.path_info)
        Logger.delete_file_if_exists(self.path_warning)
        Logger.delete_file_if_exists(self.path_error)

    def debug(self, message: str):
        print(message)
        Logger.log_to_file(message, self.path_debug)

    def info(self, message: str):
        Logger.print_with_color(message, Colors.OKBLUE)
        Logger.log_to_file(message, self.path_debug)

    def warn(self, message: str):
        Logger.print_with_color(message, Colors.WARNING)
        Logger.log_to_file(message, self.path_warning)

    def error(self, message: str):
        Logger.print_with_color(message, Colors.FAIL)
        Logger.log_to_file(message, self.path_error)

    @staticmethod
    def print_with_color(message: str, color: Colors):
        print(color + message + Colors.ENDC)

    @staticmethod
    def log_to_file(message: str, file_path: str):
        with open(file_path, "a+") as file:
            file.write(message)
            file.write("\n")

    @staticmethod
    def delete_file_if_exists(file_path: str):
        os.remove(file_path) if os.path.exists(file_path) else None
