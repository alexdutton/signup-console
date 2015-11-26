import functools
import threading

from .client import Client
from .nfc import await_nfc
from .tui import TUI

def on_input(cs):
    print cs

tui = TUI()

client = Client(tui)

finish = threading.Event()

nfc_thread = threading.Thread(target=await_nfc,
                              args=(functools.partial(client.new_identifier, 'mifareId'),
                                    finish))

try:
    tui.start()
    nfc_thread.start()
    #tui.await_input(functools.partial(client.new_identifier, 'barcodeFull'), finish)
    tui.loop(functools.partial(client.new_identifier, 'barcodeFull'))
finally:
    finish.set()
    tui.finish()