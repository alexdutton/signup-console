from __future__ import absolute_import

import time

import nfc


def _connected(tag):
    pass


def await_nfc(on_input, finish):
    clf = nfc.ContactlessFrontend('usb')
    last_identifier = {None: None}
    def done():
        last_identifier[None] = None
    while not finish.is_set():
        started = time.time()
        after5s = lambda: time.time() - started > 1
        tag = clf.connect(rdwr={'on-connect': _connected}, terminate=after5s)
        if tag:
            identifier = ''.join('%02X' % ord(c) for c in reversed(tag.identifier))
            if identifier != last_identifier[None]:
                on_input(identifier, done)
                last_identifier[None] = identifier