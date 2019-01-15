"""Utilites used for hashing information throughout the app."""

import datetime
import hashlib
import json


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        else:
            return super(DateEncoder, self).default(obj)


def hash_dict(d):
    """Return a hash of a dict that is unique for a given dict."""
    s = json.dumps(d, sort_keys=True, separators=(',', ':'), cls=DateEncoder)
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()
