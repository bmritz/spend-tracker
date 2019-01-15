"""Tests."""

from models import Message


def test_msg_to_sections():
    msg_content = """---------- Forwarded message ---------
    From: Personal Capital <support@personalcapital.com>
    Date: Sat, Jan 12, 2019 at 9:28 AM
    Subject: Your Personal Capital Daily Monitor Email
    To: bmritz@indiana.edu <bmritz@indiana.edu>

    *this

    *Section 1*
    content

    Auth : Kevs Convenience Store

    -$2.02

    *Top Gainers*

    *Top Losers*

    No gainers to show

    No losers to show

    *Accounts That Need Your Attention*

    1st Source Bank: Hsa - Individual - Ending in 8056

    Discovery Benefits: Health Savings Account
    """
    section_1 = 'content\nAuth : Kevs Convenience Store\n-$2.02'

    msg = Message(content=msg_content)
    sections = msg.sections()

    assert all(x in sections.keys()
               for x in ["Section 1", "Top Gainers", "Top Losers", "Accounts That Need Your Attention"])

    assert sections['Section 1'] == section_1
