import datetime
import enum
import inspect
from typing import TextIO


class LogOut(enum.IntEnum):
    file = 0,
    console = 1,
    console_and_file = 2


class MsgType(enum.Enum):
    info = 0,
    warn = 1,
    err = 2,
    critical = 3


class MsgTypeColor:
    info = '\033[94m'
    warn = '\033[93m'
    err = '\033[31m'
    critical = '\033[91m'
    reset = '\033[0m'
    blue = '\033[34m'
    magenta = '\033[35m'
    cyan = '\033[36m'
    green = '\033[32m'


class Log:
    log_output_level = LogOut.console
    output_file: TextIO

    def __init__(self, log_out_type):
        self.log_output_level = log_out_type

        if self.log_output_level % 2 == 0:
            output_file_path = datetime.datetime.now().strftime("%d.%m.%Y.%H.%M.log")
            self.output_file = open(output_file_path, 'w')

        self.log("Logger started! ", MsgType.info)

    def destructor(self):
        self.log("Logger closed", MsgType.info)
        if int(self.log_output_level) % 2 == 0:
            self.output_file.close()

    def log(self, msg, msg_type: MsgType):
        if self.log_output_level % 2 == 0:
            self.log_file(msg, msg_type)
        if self.log_output_level >= 1:
            self.log_console(msg, msg_type)

    def log_file(self, msg, msg_type: MsgType):
        formatted_date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        output = (f"[{formatted_date}]\t d'{inspect.stack()[0][3]}' \t"
                  f"m'{inspect.stack()[1][3]}' \t[{str(msg_type)}] ")

        self.output_file.write(output + msg + '\n')

    @staticmethod
    def log_console(msg, msg_type: MsgType):
        formatted_date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        output = (f"{MsgTypeColor.green}[{formatted_date}]\t {MsgTypeColor.blue}d'{inspect.stack()[0][3]}' \t"
                  f"{MsgTypeColor.magenta}m'{inspect.stack()[1][3]}' \t{MsgTypeColor.cyan}[{str(msg_type)}] ")

        msg_color: str = ""

        if msg_type == MsgType.info:
            msg_color = MsgTypeColor.info
        if msg_type == MsgType.warn:
            msg_color = MsgTypeColor.warn
        if msg_type == MsgType.err:
            msg_color = MsgTypeColor.err
        if msg_type == MsgType.critical:
            msg_color = MsgTypeColor.critical

        print(output + msg_color + msg + MsgTypeColor.reset)


logger = Log(LogOut.console_and_file)
