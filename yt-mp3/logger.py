import os, datetime


class Logger:
    def __init__(self, log_file_path: str, append_to_existing_logs=True):
        self.log_file_path = log_file_path

        if not append_to_existing_logs:
            self.clear_all_logs()

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
        print(full_message.encode("utf-8"))
        self.log_to_file(full_message)

    def clear_all_logs(self):
        os.remove(self.log_file_path) if os.path.exists(self.log_file_path) else None

    def log_to_file(self, message):
        with open(self.log_file_path, "ab+") as file:
            file.write(message.encode("utf8", "surrogateescape"))
            file.write("\n".encode("utf8"))