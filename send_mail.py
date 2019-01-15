"""Send email message summing up spending on groceries."""
import datetime
import logging
import os

from google.appengine.api import app_identity
from google.appengine.api import mail
import webapp2

from models import Transaction, Message, Settings


def is_grocery(txn):
    """Return boolean whether or not the input transaction is a grocery transaction."""
    content = txn.content
    grocery_keywords = ["Martin's Supermarket", "Fresh Thyme", "Wholefds"]
    return any(kwd.upper() in content.upper() for kwd in grocery_keywords)


def get_first_of_month():
    """Return a datetime.date of the first of the current month."""
    this_month = datetime.datetime.today()
    return datetime.date(this_month.year, this_month.month, 1)


def current_months_messages():
    """Return all messages for the current month from the datastore."""
    first_of_month = get_first_of_month()
    query_msgs = Message.query(Message.as_of_date >= first_of_month).order(Message.as_of_date)
    msgs = query_msgs.fetch(30)
    return msgs


def transaction_total_for_month():
    """Return the total for the month for display in the email."""

    # dedup transactions by the transactions id (doesnt include msg id)
    # the transaction's id a hash of its contents
    first_of_month = get_first_of_month()
    txns = {}
    for msg in current_months_messages():
        for txn in Transaction.query(ancestor=msg.key).fetch():
            if txn.date >= first_of_month:
                txns[txn.key.id()] = txn
    # txn amounts are negative for expenditures
    return -sum(txn.amount for txn in txns.values() if is_grocery(txn))


class EmailHandler(webapp2.RequestHandler):
    """Sends Email for recap of Month to Date spending."""

    def get(self):
        user_address = Settings.get("user_address")

        if not mail.is_email_valid(user_address):
            raise ValueError
        else:
            sender_address = Settings.get("sender_address")
            subject = 'Month to Date Grocery spending.'
            ttl = transaction_total_for_month()
            body = """Good morning B! You have spent ${:,.2f} this month on groceries.""".format(ttl)
            mail.send_mail(sender_address, user_address, subject, body)
            logging.info("An Email was sent to {}".format(user_address))


app = webapp2.WSGIApplication([
    ('/send_mail', EmailHandler),
], debug=True)
