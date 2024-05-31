import os
import bot
import log
from dotenv import load_dotenv

import persistence
import support_ticket
import user


def main():
    # Load env vars

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    # load users

    user.user_db = persistence.read_by_item()
    support_ticket.tickets = persistence.read_list('tickets.pkl')
    support_ticket.call_requests = persistence.read_list('call_requests.pkl')

    log.logger.log('Total users loaded from DB: ' + str(len(user.user_db)), log.MsgType.info, 'main')
    log.logger.log('Total tickets loaded from DB: ' + str(len(support_ticket.tickets)), log.MsgType.info, 'main')

    # init bot
    bot.init(os.environ.get("BOT_TOKEN"))
    log.logger.destructor()  # destroy logger after bot polling
    persistence.write(support_ticket.call_requests, 'call_requests.pkl')
    persistence.write(support_ticket.tickets, 'tickets.pkl')


if __name__ == '__main__':
    main()
