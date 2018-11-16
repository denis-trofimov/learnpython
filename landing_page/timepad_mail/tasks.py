"""Send timepad ticket status to mail."""
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import logging
import json
import mandrill
from django.utils import timezone
from django.conf import settings
from .models import Ticket


# Get an instance of a logger
logger = logging.getLogger(__name__)

def preprocess_webhook_payload(payload):
    if isinstance(payload, bytes):
        # 'ignore' (just leave the character out of the Unicode result)
        payload = payload.decode("utf-8", "ignore")
    process_webhook_async.delay(payload)

def beta_preprocess_webhook_payload(payload):
    """ Prepare a payload from web hook.

        :param payload: a payload from web hook
        :type payload: can be str or bytes (weird!) according to #10
    """


    """ Workaround of issue #10.
        Calling process_webhook_async.delay(payload): 
        Object of type 'bytes' is not JSON serializable.
    """
    if isinstance(payload, bytes):
        # 'ignore' (just leave the character out of the Unicode result)
        payload = payload.decode("utf-8", "ignore")

    try:
        payload_dict = json.loads(payload)
    except json.JSONDecodeError as exception:
        logger.error(f'{exception.__class__.__name__}: {exception}')
        return f'{exception.__class__.__name__}: {exception}'
        
    status = Ticket.get_status_from_raw(payload_dict.get('status_raw'))
    event_name = payload_dict.get('event_name')
    
    if not status:
        logger.info(f"{payload_dict.get('status_raw')} is not targeted.")
        return f"{payload_dict.get('status_raw')} is not targeted."
    elif not event_name in settings.WATCHED_EVENTS:
        """ If an event is not in campaign, no action required."""
        logger.info(f"{event_name} is not in campaign, no action required.")
        return f"{event_name} is not in campaign, no action required."

    process_payload_dict.delay(payload_dict)

@shared_task
def process_payload_dict(payload_dict: dict):
    "Check valid and process dictionary holding ticket values."
    ticket = Ticket.dict_deserialize(payload_dict)
    if not ticket:
        return
    elif ticket.status == Ticket.STATUS_NEW:
        return Ticket.objects.save_ticket(ticket)
    else:
        return Ticket.objects.update_ticket_status(ticket)


@shared_task
def process_webhook_async(payload: str):
    try:
        payload_dict = json.loads(payload)
    except json.JSONDecodeError as exception:
        logger.error(f'{exception.__class__.__name__}: {exception}')
        return f'{exception.__class__.__name__}: {exception}'
    status = Ticket.get_status_from_raw(payload_dict.get('status_raw'))
    event_name = payload_dict.get('event_name')
    
    if not status:
        logger.info(f"{payload_dict.get('status_raw')} is not targeted.")
        return f"{payload_dict.get('status_raw')} is not targeted."
    elif not event_name in settings.WATCHED_EVENTS:
        """ If an event is not in campaign, no action required."""
        logger.info(f"{event_name} is not in campaign, no action required.")
        return f"{event_name} is not in campaign, no action required."
    else:
        ticket = Ticket.dict_deserialize(payload_dict)
        if ticket is not None and ticket.status == Ticket.STATUS_NEW:
            return Ticket.objects.save_ticket(ticket)
        elif ticket is not None:
            return Ticket.objects.update_ticket_status(ticket)
        
def process_webhook_payload(payload: str):
    try:
        payload_dict = json.loads(payload)
    except json.JSONDecodeError as e:
        logger.error(e)
        return
    status = Ticket.get_status_from_raw(payload_dict['status_raw'])
    event_name = payload_dict['event_name']
    
    if not status:
        logger.info(f"{payload_dict['status_raw']} is not targeted.")
    elif not event_name in settings.WATCHED_EVENTS:
        """ If an event is not in campaign, no action required."""
        logger.info(f"{event_name} is not in campaign, no action required.")
    else:
        ticket = Ticket.dict_deserialize(payload_dict)
        if ticket and ticket.status == Ticket.STATUS_NEW:
            return ticket, Ticket.objects.save_ticket(ticket)
        elif ticket:
            return ticket, Ticket.objects.update_ticket_status(ticket)
        return ticket