import json
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from .send_mail_mandrill import (
    send_mail, _create_html_table_from_dict, send_template)
from .models import Ticket, TicketQuerySet

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
    "event_name": "\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435",
    "event_city": "\u0411\u0435\u0437 \u0433\u043e\u0440\u043e\u0434\u0430",
    "event_place": "",
    "hook_generated_at": "2018-10-11 00:45:54",
    "hook_guid": "710f9dbf-419b-409d-8b33-c265e6b0173d",
    "hook_resend": 2
}
"""

class MandrillSendTest(SimpleTestCase):
    """ Tests for send a transactional messages through Mandrill."""
    test_email = "denistrofimov@pythonmachinelearningcv.com"
    test_surname = "Трофимов"
    test_name = "Денис"

    def test_create_html_table_from_dict(self):
        """ Create HTML with sutable data from payload."""
        payload = {"event_id": 830329, "order_id": "17862035"}
        html = _create_html_table_from_dict(payload)
        self.assertInHTML("event_id", html)
        self.assertInHTML("830329", html)
        self.assertInHTML("order_id", html)
        self.assertInHTML("17862035", html)

    def deprecated_test_send_mail(self):
        """ Test for send a new transactional message through Mandrill using 
            real timepad webhook json data.
        """
        payload = json.loads(TIMEPAD_PAYLOAD)
        result = send_mail(payload)
        print(result)
        self.assertEqual(result[0]['status'], 'sent')

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


class TicketQuerySetTest(TestCase):

    def test_dict_deserialize(self):
        data = json.loads(TIMEPAD_PAYLOAD)
        ticket = Ticket.objects.dict_deserialize(data)
        naive_datetime = timezone.datetime.strptime(
            "2018-10-11 00:45:53", '%Y-%m-%d %H:%M:%S'
        )
        current_tz = timezone.get_current_timezone()
        local_dt = current_tz.localize(naive_datetime)

        self.assertEqual(ticket.order_id, 17862035)
        self.assertEqual(ticket.event_id, 830329)
        self.assertEqual(ticket.status, Ticket.STATUS_NEW)
        self.assertEqual(ticket.reg_date, local_dt)
        self.assertEqual(ticket.email, EMAIL)
        self.assertEqual(ticket.name, NAME)
        self.assertEqual(ticket.surname, SURNAME)
        self.assertEqual(ticket.printed_id, "22398586:56559903")

    def test_create_ticket(self):
        data = json.loads(TIMEPAD_PAYLOAD)
        ticket = Ticket.objects.dict_deserialize(data)
        new_ticket = Ticket.objects.create_ticket(ticket)
        check = Ticket.objects.filter(
            order_id=ticket.order_id, 
            event_id=ticket.event_id
        ).exists()
        self.assertEqual(check, True)
        print(new_ticket)
