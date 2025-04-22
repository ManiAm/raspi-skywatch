# Author: Mani Amoozadeh
# Email: mani.amoozadeh2@gmail.com
# Description: REST client for hexdb.io

import getpass
import logging
import inspect

from rest_client import REST_API_Client
import models_redis

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


class HEXDB_REST_API_Client(REST_API_Client):

    def __init__(self,
                 host=None,
                 port=None,
                 api_ver=None,
                 base=None,
                 user=getpass.getuser()):

        super().__init__(host, port, api_ver, base, user)


    def get_aircraft_information(self, icao_hex_code):
        """
            Retrieve aircraft information using ICAO 24-bit address.
            For example, icao_hex_code=4010EE returns:

                {
                    "ModeS": "4010EE",
                    "Registration": "G-EZBZ",
                    "Manufacturer": "Airbus",
                    "ICAOTypeCode": "A319",
                    "Type": "A319 111",
                    "RegisteredOwners": "easyJet UK",
                    "OperatorFlagCode": "EZY"
                }
        """

        frame = inspect.currentframe()
        cached = models_redis.get_from_cache(frame)
        if cached:
            return True, cached

        url = f"{self.baseurl}/aircraft/{icao_hex_code}"

        status, output = self.request("GET", url)
        if not status:
            return False, output

        models_redis.set_to_cache(frame, output)

        return True, output


    def get_airport_info_icao(self, icao_code):
        """
            Get airport info from ICAO code.
            For example, icao_code=KLAX returns:

                {
                    "country_code": "US",
                    "region_name": "California",
                    "iata": "LAX",
                    "icao": "KLAX",
                    "airport": "Los Angeles International Airport",
                    "latitude": 33.9425,
                    "longitude": -118.408
                }
        """

        frame = inspect.currentframe()
        cached = models_redis.get_from_cache(frame)
        if cached:
            return True, cached

        url = f"{self.baseurl}/airport/icao/{icao_code}"

        status, output = self.request("GET", url)
        if not status:
            return False, output

        models_redis.set_to_cache(frame, output)

        return True, output


    def get_airport_info_iata(self, iata_code):
        """
            Get airport info from IATA code.
        """

        frame = inspect.currentframe()
        cached = models_redis.get_from_cache(frame)
        if cached:
            return True, cached

        url = f"{self.baseurl}/airport/iata/{iata_code}"

        status, output = self.request("GET", url)
        if not status:
            return False, output

        models_redis.set_to_cache(frame, output)

        return True, output


    def get_route_info_icao(self, callsign):
        """
            Get flight route info from callsign in ICAO-style.
            For example, callsign=UAL1791 returns:

                {
                    'flight': 'UAL1791'
                    'route': 'KIAH-KLAX' -------> KIAH = Houston, KLAX = Los Angeles
                    'updatetime': 1534967601
                }
        """

        url = f"{self.baseurl}/route/icao/{callsign}"

        status, output = self.request("GET", url)
        if not status:
            return False, output

        return True, output


    def get_route_info_iata(self, callsign):
        """
            Get flight route info from callsign in IATA-style.
            For example, callsign=UAL1791 returns:

                {
                    'flight': 'UAL1791'
                    'route': 'IAH-LAX' -------> IAH = Houston, LAX = Los Angeles
                    'updatetime': 1534967601
                }
        """

        url = f"{self.baseurl}/route/iata/{callsign}"

        status, output = self.request("GET", url)
        if not status:
            return False, output

        return True, output


if __name__ == "__main__":

    hexdb = HEXDB_REST_API_Client(host="hexdb.io/api", api_ver="v1")

    status, output1 = hexdb.get_aircraft_information("4010EE")
    status, output2 = hexdb.get_aircraft_information("A68631")
    status, output3 = hexdb.get_aircraft_information("A12F52")

    status, output1 = hexdb.get_airport_info_icao(icao_code="KLAX")
    status, output2 = hexdb.get_airport_info_iata(iata_code="LAX")

    status, output1 = hexdb.get_route_info_icao(callsign="UAL1791")
    status, output2 = hexdb.get_route_info_iata(callsign="UAL1791")
