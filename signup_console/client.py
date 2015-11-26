import json
import requests
import requests_negotiate

class Client(object):
    def __init__(self, ui):
        self.ui = ui
        self.session = requests.Session()
        self.session.auth = requests_negotiate.HTTPNegotiateAuth(preempt=True)
        self.base_url = 'https://signup-dev.it.ox.ac.uk/signup/event/fd5a51b2bbe74d53a26b20ba79646aaa'

    def new_identifier(self, scheme, value, done=None):
        self.ui.set_loading(True)
        url = self.base_url + '/seen/add'
        response = self.session.post(url,
                                     data=json.dumps([{scheme: value}]))
        self.ui.set_loading(False)
        self.ui.show_result(response.json()['results'][0], done)
        ##self.ui.show_identifier(scheme, value)