# Author: Mani Amoozadeh
# Email: mani.amoozadeh2@gmail.com
# Description: REST client for planespotters.net

# Check Terms of use: https://www.planespotters.net/photo/api

import getpass
import logging

from rest_client import REST_API_Client

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


class Plane_Spotters_REST_API_Client(REST_API_Client):

    def __init__(self,
                 host=None,
                 port=None,
                 api_ver=None,
                 base=None,
                 user=getpass.getuser()):

        super().__init__(host, port, api_ver, base, user)


    def get_aircraft_image(self, hex):

        url = f"{self.baseurl}/photos/hex/{hex}"

        status, output = self.request("GET", url)
        if not status:
            return False, output

        return True, output


if __name__ == "__main__":

    ps_h = Plane_Spotters_REST_API_Client(host="api.planespotters.net/pub")

    status, output = ps_h.get_aircraft_image("4010EE")
    status, output = ps_h.get_aircraft_image("44055E")
