import telegram
import log
import support_ticket
import user


async def send_to_support(invoker: telegram.User, text: str):
    ticket = support_ticket.Ticket(invoker, await user.User.get_admin())
    await ticket.send_hello_to_admin()
    support_ticket.tickets.append(ticket)
    await ticket.to_admin(text)
    log.logger.log('New ticket opened: ' + str(ticket.ticket_id) + ', admin id: ' + str(await ticket.get_admin_id()),
                   log.MsgType.info, 'external services')


async def call_user_back_request(number: str):
    log.logger.log('New call request: ' + number, log.MsgType.info, 'external services')
    support_ticket.call_requests.append(number)
