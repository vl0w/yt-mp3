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
        self.path_error = root_path + "error.log"
        self.path_warning = root_path + "warn.log"
        self.path_info = root_path + "info.log"

    def success(self, message: str):
        Logger.print_with_color(message, Colors.OKGREEN)
        Logger.log_to_file(message, self.path_info)

    def info(self, message: str):
        print(message)
        Logger.log_to_file(message, self.path_info)

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
    def log_to_file(message: str, file_path: str, ):
        with open(file_path, "a+") as file:
            file.write(message)
            file.write("\n")
