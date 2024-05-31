import telegram
import log
import support_ticket
import user


async def send_to_support(invoker: telegram.User, text: str):
    log.logger.log('New support msg: ' + text, log.MsgType.info, 'external services')
    ticket = support_ticket.Ticket(invoker, await user.User.get_admin(), text)
    await ticket.send_hello_to_admin()
    support_ticket.tickets.append(ticket)
    await ticket.to_admin(text)


async def call_user_back_request(number: str):
    log.logger.log('New call request: ' + number, log.MsgType.info, 'external services')
