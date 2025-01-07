import os, io
from square.http.auth.o_auth_2 import BearerAuthCredentials
from square.client import Client
from db_lib import add_square_id, add_dep_ide, add_dep_source, get_renter_profile
import random
import string
import logging


logging.basicConfig(filename='slog.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

logger = logging.getLogger(__name__)

client = Client(
  access_token=os.environ['SQUARE_ACCESS_TOKEN'],
  environment="sandbox"
)



def square_billing_c(id):
    c =  get_renter_profile(id)

    # no square profile
    if  c['squareid'] is None:
        return False

    if c['squareid'] != 'None':
        return True
    return False


def square_billing_cc(id):
    c =  get_renter_profile(id)

    # no square profile
    if  c['squareid'] is None:
        return None

    cc_list = get_cc(c['squareid'])

    if bool(cc_list) == True:
        return cc_list['cards'][0]['id']
    return None

def square_billing_cc_last4(id):
    c =  get_renter_profile(id)

    # no square profile
    if  c['squareid'] is None:
        return None

    cc_list = get_cc(c['squareid'])

    if bool(cc_list) == True:
        return cc_list['cards'][0]['last_4']
    return None


def add_customer(billing, profile):

    result = client.customers.create_customer(
        body = {
        "given_name": billing['fname'],
        "family_name": billing['lname'],
        "email_address": profile['email'],
        "address": {
          "address_line_1": billing['add1'],
          "address_line_2": billing['add2'],
          "locality": billing['city'],
          "administrative_district_level_1": billing['state'],
          "postal_code": billing['zip'],
          "country": "US"
        },
        # "phone_number": profile['phone'],
        "reference_id": profile['id'],
        "note": ""
        }
    )

    if result.is_success():
        add_square_id(profile['id'], result.body['customer']['id'])
        return True
    elif result.is_error():
        raise Exception(result)



def get_cc(cust_id):
    result = client.cards.list_cards(
        customer_id = cust_id
    )

    if result.is_success():
        logger.debug(cust_id)
        logger.debug(result.body)
        return result.body

    elif result.is_error():
        print(result.errors)

    return None

def get_reservation_deposit(cust_id):
    result = client.cards.list_cards(
        customer_id = cust_id
    )

    if result.is_success():
        logger.debug(cust_id)
        logger.debug(result.body)
        return result.body

    elif result.is_error():
        print(result.errors)

    return None


def start_deposit(res_id, square_id, source_id):

    i_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

    add_dep_ide(res_id, i_key)

    result = client.payments.create_payment(
      body = {
        "source_id": source_id,
        "idempotency_key": i_key,
        "amount_money": {
          "amount": 100,
          "currency": "USD"
        },
        "autocomplete": False,
        "customer_id": square_id,
        "location_id": "LRBMFJC7X2GHK",
        "accept_partial_authorization": False
      }
    )

    if result.is_success():
        result
        add_dep_source(res_id, result.body['payment']['id'])
        print(result.body)
    elif result.is_error():
        print(result.errors)


def add_cc(cust_id, source_id):
    source_id='cnon:card-nonce-ok'
    result = client.cards.create_card(
            body = {
                "idempotency_key": ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
                "source_id": source_id,
                "card": {
                "customer_id": cust_id
            }
        }
    )

    if result.is_success():
        print(result.body)

    elif result.is_error():
        print(result.errors)
