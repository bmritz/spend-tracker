# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START log_sender_handler]
import logging

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext import ndb
from google.appengine.ext.ndb.google_imports import datastore_errors

from models import Message, Transaction
import webapp2

from hashing_utils import hash_dict


class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):

        msg = Message.from_mail_message(mail_message)
        logging.info("Received a message with key: " + msg.key.id())
        msg.put()
        for txn in msg.parse_transaction_info():
            txn_key_name = hash_dict(txn)
            try:
                txn = Transaction.get_or_insert(txn_key_name, parent=msg.key, **txn)
            except datastore_errors.BadValueError:
                logging.error("Transaction not parsable. Unexpected Datatypes.")


app = webapp2.WSGIApplication([LogSenderHandler.mapping()], debug=True)
