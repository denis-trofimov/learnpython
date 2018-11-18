import json
from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from django.conf import settings
from .senders import (
    send_mail, _create_html_table_from_dict, send_template)
from .models import Order, Ticket
from .tasks import process_webhook_payload, process_webhook_payload_synchro

EMAIL = "denistrofimov@pythonmachinelearningcv.com"
SURNAME = "Трофимов"
NAME = "Денис"
TIMEPAD_PAYLOAD = """
{
    "id": "22398586:56559903",
    "event_id": 830329,
    "organization_id": 143309,
    "order_id": "17862035",
    "reg_date": "2018-10-11 00:45:53",
    "reg_id": 1993954,
    "status": "\u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e",
    "status_raw": "booked",
    "email": "denistrofimov@pythonmachinelearningcv.com",
    "surname": "Трофимов",
    "name": "Денис",
    "attended": false,
    "code": "56559903",
    "barcode": "1000565599031",
    "price_nominal": "0",
    "answers": [
        {
            "id": 3518729,
            "type": "text",
            "name": "E-mail",
            "mandatory": null,
            "value": "denistrofimov@pythonmachinelearningcv.com"
        },
        {
            "id": 3518730,
            "type": "text",
            "name": "\u0424\u0430\u043c\u0438\u043b\u0438\u044f",
            "mandatory": null,
            "value": "denistrofimov"
        },
        {
            "id": 3518731,
            "type": "text",
            "name": "\u0418\u043c\u044f",
            "mandatory": null,
            "value": "denistrofimov"
        }
    ],
    "aux": {
        "use_ticket_remind": "1"
    },
    "org_name": "PythonMachineLearningCV",
    "event_name": "Learn Python 11",
    "event_city": "\u0411\u0435\u0437 \u0433\u043e\u0440\u043e\u0434\u0430",
    "event_place": "",
    "hook_generated_at": "2018-10-11 00:45:54",
    "hook_guid": "710f9dbf-419b-409d-8b33-c265e6b0173d",
    "hook_resend": 2
}
"""

class SendersTest(SimpleTestCase):
    """ Tests for send a transactional messages through Mandrill."""
    test_email = "denistrofimov@pythonmachinelearningcv.com"
    test_surname = "Трофимов"
    test_name = "Денис"

    def test_send_template_ticket_success(self):
        """ Test for send a new message through Mandrill using a template.

            result = [
                {
                    'email': 'denistrofimov@pythonmachinelearningcv.com',
                    'status': 'sent', 
                    '_id': 'd32e79d1922a4a34ae89d7cfc27dd246', 
                    'reject_reason': None
                }
            ]
        """
        result = send_template(
            template_name="ticket-success",
            email=self.test_email,
            surname=self.test_surname,
            name=self.test_name,
        )
        self.assertEqual(result[0]['status'], 'sent')
        self.assertEqual(result[0]['reject_reason'], None)
        self.assertEqual(result[0]['email'], self.test_email)

    def test_send_template_ticket_cancel(self):
        " Test for send a new message through Mandrill using a template."
        result = send_template(
            template_name="ticket-cancel",
            email=self.test_email,
            surname=self.test_surname,
            name=self.test_name,
        )
        self.assertEqual(result[0]['status'], 'sent')
        self.assertEqual(result[0]['reject_reason'], None)
        self.assertEqual(result[0]['email'], self.test_email)

    def test_send_template_ticket_creation(self):
        " Test for send a new message through Mandrill using a template."
        result = send_template(
            template_name="ticket-creation",
            email=self.test_email,
            surname=self.test_surname,
            name=self.test_name,
            vars=[
                {
                    "name": "paylink",
                    "content": "http://pay_link.python.ru",
                },
            ],
        )
        self.assertEqual(result[0]['status'], 'sent')
        self.assertEqual(result[0]['reject_reason'], None)
        self.assertEqual(result[0]['email'], self.test_email)

    def test_send_template_ticket_ticket_expiration(self):
        " Test for send a new message through Mandrill using a template."
        vars_expiration = [
            {
                "name": "paylink",
                "content": "http://pay_link.python.ru",
            },
            {
                "name": "ddate",
                "content": "31.12.2018"
            },
            {
                "name": "dtime",
                "content": "12:30"
            },
        ]
        
        for digit in ('1', '2', '3'):
            result = send_template(
                template_name="ticket-expiration{0}".format(digit),
                email=self.test_email,
                surname=self.test_surname,
                name=self.test_name,
                vars=vars_expiration
            )
            self.assertEqual(result[0]['status'], 'sent')
            self.assertEqual(result[0]['reject_reason'], None)
            self.assertEqual(result[0]['email'], self.test_email)


class TicketTest(TestCase):
    def setUp(self):
        "Create new ticket."
        self.ticket_dict = {
            "id": "22398586:56559903",
            "event_id": 830329,
            "order_id": "17862035",
            "reg_date": "2018-10-11 00:45:53",
            "status_raw": "booked",
            "email": "denistrofimov@pythonmachinelearningcv.com",
            "surname": "Трофимов",
            "name": "Денис",
            "event_name": "Learn Python 11",
        }
        
    def test_dict_deserialize(self):
        data = json.loads(TIMEPAD_PAYLOAD)
        ticket = Ticket.dict_deserialize(data)
        self.assertEqual(ticket.order_id, int(data['order_id']))
        self.assertEqual(ticket.event_id, int(data['event_id']))
        self.assertEqual(ticket.status, Ticket.STATUS_NEW)
        self.assertEqual(
            ticket.reg_date, 
            Ticket.reg_date_to_datatime(data['reg_date'])
        )
        self.assertEqual(ticket.email, data['email'])
        self.assertEqual(ticket.name, data['name'])
        self.assertEqual(ticket.surname, data['surname'])
        self.assertEqual(ticket.printed_id,  data['id'])

    def test_save_ticket(self):
        data = json.loads(TIMEPAD_PAYLOAD)
        ticket = Ticket.dict_deserialize(data)
        Ticket.objects.save_ticket(ticket)
        check = Ticket.objects.filter(
            order_id=ticket.order_id, 
            event_id=ticket.event_id
        ).exists()
        self.assertEqual(check, True)

        self.assertEqual(ticket.order_id, int(data['order_id']))
        self.assertEqual(ticket.event_id, int(data['event_id']))
        self.assertEqual(ticket.status, Ticket.STATUS_NEW)
        self.assertEqual(
            ticket.reg_date, 
            Ticket.reg_date_to_datatime(data['reg_date'])
        )
        self.assertEqual(ticket.email, data['email'])
        self.assertEqual(ticket.name, data['name'])
        self.assertEqual(ticket.surname, data['surname'])
        self.assertEqual(ticket.printed_id, data['id'])

    def test_send_reminder_one(self):
        self.ticket = Ticket.dict_deserialize(self.ticket_dict)
        self.ticket.reg_date = timezone.now() - timezone.timedelta(days=1, hours=1)
        self.ticket.save()
        self.assertLessEqual(timezone.timedelta(days=1), timezone.now() - self.ticket.reg_date)
        responses = Ticket.objects.send_reminder_one()
        for response in responses:
            self.assertIn(response[0]['status'], ('sent', 'queued'))
        ticket = Ticket.objects.get_ticket(self.ticket)
        self.assertEqual(ticket.status, Ticket.STATUS_REMINDED_1)

    def test_send_reminder_two(self):
        self.ticket = Ticket.dict_deserialize(self.ticket_dict)
        self.ticket.reg_date = timezone.now() - timezone.timedelta(days=2, hours=1)
        self.ticket.save()
        responses = Ticket.objects.send_reminder_two()
        for response in responses:
            self.assertIn(response[0]['status'], ('sent', 'queued'))
        ticket = Ticket.objects.get_ticket(self.ticket)
        self.assertEqual(ticket.status, Ticket.STATUS_REMINDED_2)

    def test_send_reminder_three(self):
        self.ticket = Ticket.dict_deserialize(self.ticket_dict)
        self.ticket.reg_date = timezone.now() - timezone.timedelta(hours=70)
        self.ticket.save()
        responses = Ticket.objects.send_reminder_three()
        for response in responses:
            self.assertIn(response[0]['status'], ('sent', 'queued'))
        ticket = Ticket.objects.get_ticket(self.ticket)
        self.assertEqual(ticket.status, Ticket.STATUS_REMINDED_3)

class TasksTest(TestCase):

    def test_manage_webhook_payload_booked(self):
        """ Check new ticket."""
        data = json.loads(TIMEPAD_PAYLOAD)
        data['event_name'] = settings.WATCHED_EVENTS[0]
        payload = json.dumps(data) 
        new_ticket = Ticket.dict_deserialize(data)
        response = process_webhook_payload_synchro(payload)
        self.assertIn(response[0]['status'], ('sent', 'queued'))
        self.assertEqual(response[0]['email'], new_ticket.email)

        ticket = Ticket.objects.get_ticket(new_ticket)
        self.assertEqual(ticket.order_id, int(data['order_id']))
        self.assertEqual(ticket.event_id, int(data['event_id']))
        self.assertEqual(ticket.status, Ticket.STATUS_NEW)
        self.assertEqual(
            ticket.reg_date, 
            Ticket.reg_date_to_datatime(data['reg_date'])
        )
        self.assertEqual(ticket.email, data['email'])
        self.assertEqual(ticket.name, data['name'])
        self.assertEqual(ticket.surname, data['surname'])
        self.assertEqual(ticket.printed_id, data['id'])
        self.assertEqual(ticket.event_name, data['event_name'])

    def test_manage_webhook_payload_booked_async(self):
        """ Check new ticket."""
        data = json.loads(TIMEPAD_PAYLOAD)
        data['event_name'] = settings.WATCHED_EVENTS[0]
        payload = json.dumps(data) 
        process_webhook_payload(payload)

    def test_manage_webhook_payload_booked_not_tracked(self):
        """ Check new ticket from not tracked event."""
        data = json.loads(TIMEPAD_PAYLOAD)
        data['event_name'] = 'crap'
        payload = json.dumps(data) 
        response = process_webhook_payload_synchro(payload)
        self.assertEqual(response, None)

    def test_manage_webhook_payload_status_not_tracked(self):
        """ Check new ticket from not tracked status_raw."""
        data = json.loads(TIMEPAD_PAYLOAD)
        data['status_raw'] = 'ok'
        data['event_name'] = settings.WATCHED_EVENTS[0]
        payload = json.dumps(data) 
        response = process_webhook_payload_synchro(payload)
        self.assertEqual(response, None)


class TicketUpdateAsyncTest(TestCase):
    def setUp(self):
        "Create new ticket."
        self.ticket_dict = {
            "id": "22398586:56559903",
            "event_id": 830329,
            "order_id": "17862035",
            "reg_date": "2018-10-11 00:45:53",
            "status_raw": "booked",
            "email": "denistrofimov@pythonmachinelearningcv.com",
            "surname": "Трофимов",
            "name": "Денис",
            "event_name": "Learn Python 11",
        }
        self.ticket = Ticket.dict_deserialize(self.ticket_dict)
        self.ticket.save()  
        
class TicketUpdateTest(TestCase):

    def setUp(self):
        "Create new ticket."
        self.ticket_dict = {
            "id": "22398586:56559903",
            "event_id": 830329,
            "order_id": "17862035",
            "reg_date": "2018-10-11 00:45:53",
            "status_raw": "booked",
            "email": "denistrofimov@pythonmachinelearningcv.com",
            "surname": "Трофимов",
            "name": "Денис",
            "event_name": "Learn Python 11",
        }
        self.ticket = Ticket.dict_deserialize(self.ticket_dict)
        self.ticket.save() 

    def test_manage_webhook_payload_notpaid(self):
        data = self.ticket_dict
        data['status_raw'] = 'notpaid'

        payload = json.dumps(data) 
        updated_ticket = Ticket.dict_deserialize(data)
        response = process_webhook_payload_synchro(payload)
        self.assertIn(response[0]['status'], ('sent', 'queued'))
        self.assertEqual(response[0]['email'], updated_ticket.email)
        self.assertIsInstance(updated_ticket, Ticket)
        ticket = Ticket.objects.get_ticket(updated_ticket)

        self.assertEqual(ticket.order_id, int(data['order_id']))
        self.assertEqual(ticket.event_id, int(data['event_id']))
        self.assertEqual(ticket.status, Ticket.get_status_from_raw(data['status_raw']))
        self.assertEqual(
            ticket.reg_date, 
            Ticket.reg_date_to_datatime(data['reg_date'])
        )
        self.assertEqual(ticket.email, data['email'])
        self.assertEqual(ticket.name, data['name'])
        self.assertEqual(ticket.surname, data['surname'])
        self.assertEqual(ticket.printed_id, data['id'])
        self.assertEqual(ticket.event_name, data['event_name'])

    def test_manage_webhook_payload_paid(self):
        """ Check new ticket."""
        data = self.ticket_dict
        data['status_raw'] = 'paid'
        payload = json.dumps(data) 
        updated_ticket = Ticket.dict_deserialize(data)
        response = process_webhook_payload_synchro(payload)
        self.assertIn(response[0]['status'], ('sent', 'queued'))
        self.assertEqual(response[0]['email'], updated_ticket.email)
        self.assertIsInstance(updated_ticket, Ticket)
        ticket = Ticket.objects.get_ticket(updated_ticket)

        self.assertEqual(ticket.order_id, int(data['order_id']))
        self.assertEqual(ticket.event_id, int(data['event_id']))
        self.assertEqual(ticket.status, Ticket.get_status_from_raw(data['status_raw']))
        self.assertEqual(
            ticket.reg_date, 
            Ticket.reg_date_to_datatime(data['reg_date'])
        )
        self.assertEqual(ticket.email, data['email'])
        self.assertEqual(ticket.name, data['name'])
        self.assertEqual(ticket.surname, data['surname'])
        self.assertEqual(ticket.printed_id, data['id'])
        self.assertEqual(ticket.event_name, data['event_name'])

class OrderTest(TestCase):

    def setUp(self):
        "Create new order."
        self.order_dict = json.load('order.json')
        
    def test_dict_deserialize(self):
        data = self.order_dict
        order = Order.dict_deserialize(data)
        self.assertEqual(order.order_id, int(data['id']))
        self.assertEqual(order.event_id, int(data['event']['id']))
        self.assertEqual(order.status, Order.get_status_from_raw(data['status']['name'])
        self.assertEqual(
            order.reg_date, 
            Order.reg_date_to_datatime(data['created_at'])
        )
        self.assertEqual(order.email, data['mail'])
        self.assertEqual(order.name, data["answers"]['name'])
        self.assertEqual(order.surname, data["answers"]['surname'])
        self.assertEqual(order.payment_amount, int(data['payment']['amount']))
        self.assertEqual(order.full_clean(), True)


    def test_send_reminder_one(self):
        self.order = Order.dict_deserialize(self.order_dict)
        self.order.reg_date = timezone.now() - timezone.timedelta(days=1, hours=1)
        self.order.save()
        self.assertLessEqual(timezone.timedelta(days=1), timezone.now() - self.order.reg_date)
        responses = Order.objects.send_reminder_one()
        for response in responses:
            self.assertIn(response[0]['status'], ('sent', 'queued'))
        order = Order.objects.get_order(self.order)
        self.assertEqual(order.status, Order.STATUS_REMINDED_1)

    def test_send_reminder_two(self):
        self.order = Order.dict_deserialize(self.order_dict)
        self.order.reg_date = timezone.now() - timezone.timedelta(days=2, hours=1)
        self.order.save()
        responses = Order.objects.send_reminder_two()
        for response in responses:
            self.assertIn(response[0]['status'], ('sent', 'queued'))
        order = Order.objects.get_order(self.order)
        self.assertEqual(order.status, Order.STATUS_REMINDED_2)

    def test_send_reminder_three(self):
        self.order = Order.dict_deserialize(self.order_dict)
        self.order.reg_date = timezone.now() - timezone.timedelta(hours=70)
        self.order.save()
        responses = Order.objects.send_reminder_three()
        for response in responses:
            self.assertIn(response[0]['status'], ('sent', 'queued'))
        order = Order.objects.get_order(self.order)
        self.assertEqual(order.status, Order.STATUS_REMINDED_3)


    def test_check_order_expiration1(self):
        self.order = Order.dict_deserialize(self.order_dict)
        self.order.reg_date = timezone.now() - timezone.timedelta(days=1)
        self.order.save()
        self.assertLessEqual(timezone.timedelta(hours=9), timezone.now() - self.order.reg_date)
        self.order.objects.send_reminder_one()
        order = self.order.objects.get_order(self.order)
        self.assertEqual(order.status, Order.STATUS_REMINDED_1)

