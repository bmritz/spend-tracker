"""Models for ndb database."""

import datetime
import hashlib
import logging
import re

from google.appengine.ext import ndb

from parsing_helpers import iter_sections


class Message(ndb.Model):
    """Models an individual Message entry."""
    content = ndb.TextProperty()
    sender = ndb.StringProperty()
    as_of_date = ndb.DateProperty()
    date = ndb.DateProperty(auto_now_add=True)

    @staticmethod
    def is_transaction_header(s):
        """Determine if the given string is a transaction header."""
        match = re.search('Recent transactions as of [0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}', s)
        if match:
            return True
        return False

    @classmethod
    def from_mail_message(cls, mail_message):
        plaintext_bodies = mail_message.bodies('text/plain')
        for content_type, body in plaintext_bodies:
            plaintext = body.decode()
            match = re.search('Recent transactions as of [0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}', plaintext)
            as_of_date = datetime.datetime.strptime(match.group()[-8:], '%m/%d/%y').date() if match else None
            msg_key = ndb.Key("Message", cls._hash_mail_message(mail_message))
            return cls(sender=mail_message.sender, content=plaintext, as_of_date=as_of_date, key=msg_key)

    @staticmethod
    def _hash_mail_message(mail_message):
        m = hashlib.md5()
        m.update(mail_message.sender)
        plaintext_bodies = mail_message.bodies('text/plain')
        for content_type, body in plaintext_bodies:
            m.update(body.decode())
        return m.hexdigest()

    def parse_transaction_info(self):
        """Parse information on the transactions from the plaintext message content.

        Yields:
            Dict of information about each transaction in the message content.

        """

        lines = [line.strip() for line in self.content.split("\n")]

        transaction_header_inx = next(i for i, line in enumerate(lines) if self.is_transaction_header(line))
        yr = lines[transaction_header_inx][-3:-1]
        inx = transaction_header_inx + 2

        line = lines[inx]
        while line:
            dt, acct, content, amt = re.split(r'\s{2,}', line)
            dt = datetime.datetime.strptime(dt + '/' + yr, '%m/%d/%y').date()
            amt = float(amt.replace("$", "").replace(',', ''))
            yield dict(date=dt, account=acct.strip(), content=content.strip(), amount=amt)
            inx += 1
            line = lines[inx]


class Transaction(ndb.Model):
    """Models an individual Transaction received through a Message."""
    date = ndb.DateProperty()
    account = ndb.StringProperty()
    content = ndb.StringProperty()
    amount = ndb.FloatProperty()

    def hash(self):
        return str(hash((self.date, self.account, self.content, self.amount)))

    def __str__(self):
        return "Transaction(%s, %s, %s, %s)" % (self.date, self.account, self.content, self.amount)


class Settings(ndb.Model):
    """
    Get sensitive data setting from DataStore.

    key:String -> value:String
    key:String -> Exception

    Thanks to: Martin Omander @ Stackoverflow
    https://stackoverflow.com/a/35261091/1463812
    """
    name = ndb.StringProperty()
    value = ndb.StringProperty()

    @staticmethod
    def get(name):
        retval = Settings.query(Settings.name == name).get()
        if not retval:
            raise Exception(('Setting %s not found in the database. A placeholder ' +
                             'record has been created. Go to the Developers Console for your app ' +
                             'in App Engine, look up the Settings record with name=%s and enter ' +
                             'its value in that record\'s value field.') % (name, name))
        return retval.value

    @staticmethod
    def set(name, value):
        exists = Settings.query(Settings.name == name).get()
        if not exists:
            s = Settings(name=name, value=value)
            s.put()
        else:
            exists.value = value
            exists.put()

        return True
