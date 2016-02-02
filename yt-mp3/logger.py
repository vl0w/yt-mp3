import datetime

class Logger:
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path

    def debug(self, message: str):
        self.__log_to_console_and_file(message, "DEBUG")

    def info(self, message: str):
        self.__log_to_console_and_file(message, "INFO")

    def warning(self, message: str):
        self.__log_to_console_and_file(message, "WARNING")

    def error(self, message: str):
        self.__log_to_console_and_file(message, "ERROR")

    def __log_to_console_and_file(self, message: str, level: str):
        full_message = "{0}: {1} | {2}".format(level, datetime.datetime.now(), message)
        print(full_message)
        self.__log_to_file(full_message)

    def __log_to_file(self, message):
        with open(self.log_file_path, "ab+") as file:
            file.write(message.encode("utf8", "surrogateescape"))
            file.write("\n".encode("utf8"))