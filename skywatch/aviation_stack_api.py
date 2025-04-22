# Author: Mani Amoozadeh
# Email: mani.amoozadeh2@gmail.com
# Description: REST client for aviationstack

# Check Terms of use: https://aviationstack.com/documentation

import os
import getpass
import logging

from rest_client import REST_API_Client

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


class Aviation_Stack_REST_API_Client(REST_API_Client):

    def __init__(self,
                 host=None,
                 port=None,
                 api_ver=None,
                 base=None,
                 user=getpass.getuser()):

        super().__init__(host, port, api_ver, base, user)

        self.access_token = os.getenv('AVIATION_STACK_API_TOKEN', None)


    def get_flights(self,
                    flight_status=None, # scheduled, active, landed, cancelled, incident, diverted
                    flight_date=None,
                    dep_iata=None,
                    arr_iata=None,
                    dep_icao=None,
                    arr_icao=None,
                    airline_name=None,
                    airline_iata=None,
                    airline_icao=None,
                    flight_number=None, # Filter your results by providing a flight number. Example: 2557
                    flight_iata=None,   # Filter your results by providing a flight IATA code. Example: MU2557
                    flight_icao=None):  # Filter your results by providing a flight ICAO code. Example: CES2557

        url = f"{self.baseurl}/flights"

        params = {
            "access_key": self.access_token,
            "flight_status": flight_status,
            "flight_date": flight_date,
            "dep_iata": dep_iata,
            "arr_iata": arr_iata,
            "dep_icao": dep_icao,
            "arr_icao": arr_icao,
            "airline_name": airline_name,
            "airline_iata": airline_iata,
            "airline_icao": airline_icao,
            "flight_number": flight_number,
            "flight_iata": flight_iata,
            "flight_icao": flight_icao
        }

        status, output = self.request("GET", url, params=params)
        if not status:
            return False, output

        return True, output


    def get_airports(self, search=None, limit=100, max_pages=-1):
        """
            {
                "id": "3487527",
                "gmt": "-10",
                "airport_id": "1",
                "iata_code": "AAA",
                "city_iata_code": "AAA",
                "icao_code": "NTGA",
                "country_iso2": "PF",
                "geoname_id": "6947726",
                "latitude": "-17.05",
                "longitude": "-145.41667",
                "airport_name": "Anaa",
                "country_name": "French Polynesia",
                "phone_number": null,
                "timezone": "Pacific/Tahiti"
            }
        """

        url = f"{self.baseurl}/airports"

        offset = 0
        page_num = 1
        results = []

        while True:

            params = {
                "access_key": self.access_token,
                "search": search,
                "limit": limit,
                "offset": offset
            }

            status, output = self.request("GET", url, params=params)
            if not status:
                return False, output

            data = output.get("data", [])
            results.extend(data)

            pagination = output.get("pagination", {})
            count = pagination.get("count", 0)
            total = pagination.get("total", 0)

            if len(results) >= total:
                break

            if max_pages != -1 and page_num >= max_pages:
                break

            page_num += 1
            offset += count

        return True, results


    def get_airlines(self, search=None, limit=100, max_pages=-1):
        """
            {
                "id": "4439746",
                "fleet_average_age": "6.3",
                "airline_id": "12",
                "callsign": "TURKISH",
                "hub_code": "IST",
                "iata_code": "TK",
                "icao_code": "THY",
                "country_iso2": "TR",
                "date_founded": "1933",
                "iata_prefix_accounting": "235",
                "airline_name": "THY - Turkish Airlines",
                "country_name": "Turkey",
                "fleet_size": "285",
                "status": "active",
                "type": "scheduled"
            }
        """

        url = f"{self.baseurl}/airlines"

        offset = 0
        page_num = 1
        results = []

        while True:

            params = {
                "access_key": self.access_token,
                "search": search,
                "limit": limit,
                "offset": offset
            }

            status, output = self.request("GET", url, params=params)
            if not status:
                return False, output

            data = output.get("data", [])
            results.extend(data)

            pagination = output.get("pagination", {})
            count = pagination.get("count", 0)
            total = pagination.get("total", 0)

            if len(results) >= total:
                break

            if max_pages != -1 and page_num >= max_pages:
                break

            page_num += 1
            offset += count

        return True, results


    def get_airplanes(self, search=None, limit=100, max_pages=-1):
        """
            {
                "id": "6454205",
                "iata_type": "ATR72-500",
                "airplane_id": "95",
                "airline_iata_code": "2Z",
                "iata_code_long": "AT75",
                "iata_code_short": "AT7",
                "airline_icao_code": null,
                "construction_number": "572",
                "delivery_date": "1999-10-03",
                "engines_count": "2",
                "engines_type": "TURBOPROP",
                "first_flight_date": "1998-09-01",
                "icao_code_hex": "E48D80",
                "line_number": null,
                "model_code": "ATR72-500",
                "registration_number": "PR-PDH",
                "test_registration_number": null,
                "plane_age": "19",
                "plane_class": null,
                "model_name": "ATR 72",
                "plane_owner": "Aircraft International Renting Ltd",
                "plane_series": "212A",
                "plane_status": "active",
                "production_line": "ATR 42/72",
                "registration_date": "2013-11-08",
                "rollout_date": "0000-00-00"
            }
        """

        url = f"{self.baseurl}/airplanes"

        offset = 0
        page_num = 1
        results = []

        while True:

            params = {
                "access_key": self.access_token,
                "search": search,
                "limit": limit,
                "offset": offset
            }

            status, output = self.request("GET", url, params=params)
            if not status:
                return False, output

            data = output.get("data", [])
            results.extend(data)

            pagination = output.get("pagination", {})
            count = pagination.get("count", 0)
            total = pagination.get("total", 0)

            if len(results) >= total:
                break

            if max_pages != -1 and page_num >= max_pages:
                break

            page_num += 1
            offset += count

        return True, results


    def get_aircraft_types(self, search=None, limit=100, max_pages=-1):
        """
            'id' = '22228'
            'iata_code' = '100'
            'aircraft_name' = 'Fokker 100'
            'plane_type_id' = '1'
        """

        url = f"{self.baseurl}/aircraft_types"

        offset = 0
        page_num = 1
        results = []

        while True:

            params = {
                "access_key": self.access_token,
                "search": search,
                "limit": limit,
                "offset": offset
            }

            status, output = self.request("GET", url, params=params)
            if not status:
                return False, output

            data = output.get("data", [])
            results.extend(data)

            pagination = output.get("pagination", {})
            count = pagination.get("count", 0)
            total = pagination.get("total", 0)

            if len(results) >= total:
                break

            if max_pages != -1 and page_num >= max_pages:
                break

            page_num += 1
            offset += count

        return True, results


    def get_countries(self, search=None, limit=100, max_pages=-1):
        """
            {
                "id": "83665",
                "capital": "Andorra la Vella",
                "currency_code": "EUR",
                "fips_code": "AN",
                "country_iso2": "AD",
                "country_iso3": "AND",
                "continent": "EU",
                "country_id": "1",
                "country_name": "Andorra",
                "currency_name": "Euro",
                "country_iso_numeric": "20",
                "phone_prefix": "376",
                "population": "84000"
            }
        """

        url = f"{self.baseurl}/countries"

        offset = 0
        page_num = 1
        results = []

        while True:

            params = {
                "access_key": self.access_token,
                "search": search,
                "limit": limit,
                "offset": offset
            }

            status, output = self.request("GET", url, params=params)
            if not status:
                return False, output

            data = output.get("data", [])
            results.extend(data)

            pagination = output.get("pagination", {})
            count = pagination.get("count", 0)
            total = pagination.get("total", 0)

            if len(results) >= total:
                break

            if max_pages != -1 and page_num >= max_pages:
                break

            page_num += 1
            offset += count

        return True, results


    def get_cities(self, search=None, limit=100, max_pages=-1):
        """
            {
                "id": "3157947",
                "gmt": "-10",
                "city_id": "1",
                "iata_code": "AAA",
                "country_iso2": "PF",
                "geoname_id": null,
                "latitude": "-17.05",
                "longitude": "-145.41667",
                "city_name": "Anaa",
                "timezone": "Pacific/Tahiti"
            }
        """

        url = f"{self.baseurl}/cities"

        offset = 0
        page_num = 1
        results = []

        while True:

            params = {
                "access_key": self.access_token,
                "search": search,
                "limit": limit,
                "offset": offset
            }

            status, output = self.request("GET", url, params=params)
            if not status:
                return False, output

            data = output.get("data", [])
            results.extend(data)

            pagination = output.get("pagination", {})
            count = pagination.get("count", 0)
            total = pagination.get("total", 0)

            if len(results) >= total:
                break

            if max_pages != -1 and page_num >= max_pages:
                break

            page_num += 1
            offset += count

        return True, results


if __name__ == "__main__":

    as_h = Aviation_Stack_REST_API_Client(host="api.aviationstack.com", api_ver="v1")

    status, output = as_h.get_flights(flight_number="UA549")

    bla = 0
