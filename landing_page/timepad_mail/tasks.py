"""Send timepad ticket status to mail."""
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import logging
import json
import mandrill
from django.utils import timezone
from django.conf import settings
from .models import Ticket, Order, Hook


# Get an instance of a logger
logger = logging.getLogger(__name__)

def preprocess_webhook_payload(payload: str):
    """ Prepare a payload from web hook.

        :param payload: a payload from web hook
        :returm: a dictionary holding ticket values.
    """
    try:
        payload_dict = json.loads(payload)
    except json.JSONDecodeError as exception:
        logger.error(f'{exception.__class__.__name__}: {exception}')
        return

    status = Ticket.get_status_from_raw(payload_dict.get('status_raw'))
    event_name = payload_dict.get('event_name')
    
    if not status:
        logger.info(f"{payload_dict.get('status_raw')} is not targeted.")
        return
    elif not event_name in settings.WATCHED_EVENTS:
        """ If an event is not in campaign, no action required."""
        logger.info(f"{event_name} is not in campaign, no action required.")
        return
    return payload_dict

@shared_task
def process_payload_dict(payload_dict: dict):
    """ Check valid and process a dictionary holding ticket values.

        :param payload_dict: a dictionary holding ticket values.
        :return: a ManDrill server response or None on error.
    """
    ticket = Ticket.dict_deserialize(payload_dict)
    if not ticket:
        return
    elif ticket.status == Ticket.STATUS_NEW:
        return Ticket.objects.save_ticket(ticket)
    else:
        return Ticket.objects.update_ticket_status(ticket)

def process_webhook_payload(payload: str):
    """ Process payload from web hook.

        :param payload: a payload from web hook.
        :return: a ManDrill server response or None on error.
    """
    payload_dict = preprocess_webhook_payload(payload)
    if not payload_dict or not isinstance(payload_dict, dict):
        return
    "Check valid and process dictionary holding ticket values."
    process_payload_dict.delay(payload_dict)

def process_webhook_payload_synchro(payload: str):
    """ Process payload from web hook.

        :param payload: a payload from web hook.
        :return: a ManDrill server response or None on error.
    """
    payload_dict = preprocess_webhook_payload(payload)
    if not payload_dict or not isinstance(payload_dict, dict):
        return
    "Check valid and process dictionary holding ticket values."
    return process_payload_dict(payload_dict)

def preprocess_order_payload(payload: str):
    """ Prepare a payload from web hook with an order.

        :param payload: a payload from web hook
        :returm: a dictionary holding order values.
    """
    try:
        payload_dict = json.loads(payload)
    except json.JSONDecodeError as exception:
        logger.error(f'{exception.__class__.__name__}: {exception}')
        return

    status = Order.get_status_from_raw(payload_dict.get('status').get('name'))
    event_id = payload_dict.get('event').get('id')
    guid = payload_dict.get('hook_guid')
    if not status:
        logger.info(f"{status} is not targeted.")
        return
    elif not event_id in settings.WATCHED_EVENT_ID:
        """ If an event is not in campaign, no action required."""
        logger.info(f"{event_id} is not in campaign, no action required.")
        return
    
    """ Create hook if not exists, else abort processing."""
    if Hook.objects.guid_exists(guid):
        logger.info(f"Hook {guid} is repeating.")
        return
    else:
        hook = Hook(guid=guid)
        hook.save()

    return payload_dict

@shared_task
def process_order_dict(payload_dict: dict):
    """ Check valid and process a dictionary holding order values.

        :param payload_dict: a dictionary holding order values.
        :return: a ManDrill server response or None on error.
    """
    order = Order.dict_deserialize(payload_dict)
    if not order:
        return
    elif order.status == Order.STATUS_NEW:
        return Order.objects.save_ticket(order)
    else:
        return Order.objects.update_ticket_status(order)

@shared_task
def process_order_payload(payload: str):
    """ Process payload from web hook with an order.

        :param payload: a payload from web hook.
        :return: a ManDrill server response or None on error.
    """
    payload_dict = preprocess_order_payload(payload)
    if not payload_dict or not isinstance(payload_dict, dict):
        return
    "Check valid and process dictionary holding ticket values."
