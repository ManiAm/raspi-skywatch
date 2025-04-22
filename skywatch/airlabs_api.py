# Author: Mani Amoozadeh
# Email: mani.amoozadeh2@gmail.com
# Description: REST client for AirLabs

# Check Terms of use: https://airlabs.co/docs/#docs_Introduction

import os
import getpass
import logging

from rest_client import REST_API_Client

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


class AirLabs_REST_API_Client(REST_API_Client):

    def __init__(self,
                 host=None,
                 port=None,
                 api_ver=None,
                 base=None,
                 user=getpass.getuser()):

        super().__init__(host, port, api_ver, base, user)

        self.access_token = os.getenv('AIRLAB_API_TOKEN', None)


    def get_flights(self):

        pass


if __name__ == "__main__":

    al_h = AirLabs_REST_API_Client(host="airlabs.co/api/", api_ver="v9")

    status, output = al_h.get_flights()

    bla = 0
