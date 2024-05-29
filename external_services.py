import log


def send_to_support(text: str):
    log.logger.log('New support msg: ' + text, log.MsgType.info, 'external services')


def call_user_back_request(number: str):
    log.logger.log('New call request: ' + number, log.MsgType.info, 'external services')
