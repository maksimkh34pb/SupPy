import datetime
import enum
import traceback
from typing import TextIO


class LogOut(enum.IntEnum):
    file = 0,
    console = 1,
    console_and_file = 2


class MsgType(enum.Enum):
    info = 0,
    success = 1
    warn = 2,
    err = 3,
    critical = 4


class MsgTypeColor:
    info = '\033[94m'
    warn = '\033[93m'
    success = '\033[32m'
    err = '\033[31m'
    critical = '\033[91m'
    reset = '\033[0m'
    blue = '\033[34m'
    magenta = '\033[35m'
    cyan = '\033[36m'


def get_traceback():
    lines = []
    result = []

    for line in traceback.format_stack():
        if line.__contains__('SupPy'):
            if not line.__contains__('<module>'):
                lines.append(line)

    for line in lines:
        result.append(line.split('\n  ')[0].split('in ')[-1])

    result = '->'.join(result[:-3])
    if len(result) > 47:
        result = '...' + result[-47:]

    return result


class Log:
    log_output_level = LogOut.console
    output_file: TextIO

    def __init__(self, log_out_type):
        self.log_output_level = log_out_type

        if self.log_output_level % 2 == 0:
            output_file_path = datetime.datetime.now().strftime("%d.%m.%Y.%H.%M.log")
            self.output_file = open(output_file_path, 'w')

        self.log("Logger started! \n", MsgType.success, 'Logger')

    def destructor(self):
        self.log("Logger closed", MsgType.success, 'Logger', '\n')
        if int(self.log_output_level) % 2 == 0:
            self.output_file.close()

    def log(self, msg, msg_type: MsgType, module_name: str, prefix: str = ''):
        if self.log_output_level % 2 == 0:
            self.log_file(msg, msg_type, module_name, prefix)
        if self.log_output_level >= 1:
            self.log_console(msg, msg_type, module_name, prefix)

    def log_file(self, msg, msg_type: MsgType, module_name: str, prefix: str = ''):
        formatted_date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        output = (prefix + f"[{formatted_date}]\t d'{get_traceback()}' \t"
                  f"m'{module_name}' \t[{str(msg_type)}] ")

        self.output_file.write(output + msg + '\n')

    @staticmethod
    def log_console(msg, msg_type: MsgType, module_name: str, prefix: str = ''):
        formatted_date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        output = (prefix + f"{MsgTypeColor.success}[{formatted_date}]\t {MsgTypeColor.blue}d'{get_traceback()}' \t"
                  f"{MsgTypeColor.magenta}m'{module_name}' \t{MsgTypeColor.cyan}[{str(msg_type)}] ")

        msg_color: str = ""

        if msg_type == MsgType.info:
            msg_color = MsgTypeColor.info
        if msg_type == MsgType.success:
            msg_color = MsgTypeColor.success
        if msg_type == MsgType.warn:
            msg_color = MsgTypeColor.warn
        if msg_type == MsgType.err:
            msg_color = MsgTypeColor.err
        if msg_type == MsgType.critical:
            msg_color = MsgTypeColor.critical

        print(output + msg_color + msg + MsgTypeColor.reset)


logger = Log(LogOut.console)
