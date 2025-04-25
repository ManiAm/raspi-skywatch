#!/usr/bin/env python3

# Author: Mani Amoozadeh
# Email: mani.amoozadeh2@gmail.com
# Description: SkyWatch application

import sys
import os
import signal
import socket
import gc
import queue
import threading
import csv
import json
import logging
import time
import redis
from geopy.distance import geodesic
from gpsdclient import GPSDClient

import models_sql
from hexdb_api import HEXDB_REST_API_Client
from plane_spotters_api import Plane_Spotters_REST_API_Client
from discord_webhook import Discord_Webhook
import get_aircraft_svg
import utility

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


class SkyWatch():

    def __init__(self,
                 alert_radius_km=10,  # Alert if aircraft within this distance
                 home_lat=None,
                 home_lon=None,
                 gpsd_host="localhost",
                 gpsd_port=2947,
                 dump1090_host="localhost",
                 dump1090_port=30003,
                 csv_save=True,
                 csv_path="aircraft_log.csv",
                 monitor_interval=10):

        self.alert_radius_km = alert_radius_km
        self.home_lat = home_lat
        self.home_lon = home_lon

        self.gpsd_host = gpsd_host
        self.gpsd_port = gpsd_port

        self.dump1090_host = dump1090_host
        self.dump1090_port = dump1090_port

        self.csv_save = csv_save
        self.csv_path = csv_path

        self.monitor_interval = monitor_interval

        ########

        self.running = True

        self.csv_file = None
        self.csv_writer = None

        self.msg_queue = queue.Queue(maxsize=100)
        self.msg_rate_produce = 0
        self.msg_rate_consume = 0

        self.icao_code_hex_missing = set()
        self.max_observed_distance_km = 0

        self.sbs_field_names = [
            "message_type",
            "transmission_type",
            "session_id",
            "aircraft_id",
            "hex_ident",
            "flight_id",
            "generated_date",
            "generated_time",
            "logged_date",
            "logged_time",
            "callsign",
            "altitude",
            "ground_speed",
            "track",
            "latitude",
            "longitude",
            "vertical_rate",
            "squawk",
            "alert",
            "emergency",
            "spi",
            "is_on_ground"
        ]

        ########

        if not self.home_lat and not self.home_lon:
            self.home_lat, self.home_lon = self.get_coordinates_gpsd()

        if not self.home_lat or not self.home_lon:
            log.error("Home coordinates are not set properly!")
            sys.exit(2)

        log.info("Latitude: %s, Longitude: %s", self.home_lat, self.home_lon)

        if self.csv_save:
            self.init_csv()

        self.redis = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        self.postgresql_session = models_sql.Session(bind=models_sql.engine)

        self.hexdb = HEXDB_REST_API_Client(host="hexdb.io/api", api_ver="v1")
        self.ps_h = Plane_Spotters_REST_API_Client(host="api.planespotters.net/pub")

        self.discord = Discord_Webhook(host="discord.com", base="api/webhooks")

    ###############################################################################

    def get_coordinates_gpsd(self):

        with GPSDClient(host=self.gpsd_host, port=self.gpsd_port) as client:

            # TPV = Time-Position-Velocity
            for result in client.json_stream(filter=["TPV"]):

                data = json.loads(result)

                lat = data.get("lat", None)
                lon = data.get("lon", None)

                if lat is not None and lon is not None:
                    return lat, lon


    def init_csv(self):

        log.info("Initializing CSV.")

        self.csv_file = open(self.csv_path, mode='a', newline='')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.sbs_field_names)

        # Write header if file is new
        if os.stat(self.csv_path).st_size == 0:
            self.csv_writer.writeheader()

    ###############################################################################

    def start(self):

        monitor_thread = threading.Thread(target=self.monitor_queue)
        monitor_thread.start()

        receive_thread = threading.Thread(target=self.receive_thr)
        receive_thread.start()

        self.consume()


    def stop(self):

        log.info("Stopping SkyWatch...")
        self.running = False


    def monitor_queue(self):

        while self.running:

            time.sleep(self.monitor_interval)

            log.info(
                "[Monitor] Backlog Queue size: \033[94m%4d\033[0m  "
                "Receive Rate: \033[94m%7.2f\033[0m msg/sec  "
                "Process Rate: \033[94m%7.2f\033[0m msg/sec  "
                "Max Observed Distance: \033[94m%7.2f\033[0m km",
                self.msg_queue.qsize(),
                self.msg_rate_produce,
                self.msg_rate_consume,
                self.max_observed_distance_km
            )

            if self.icao_code_hex_missing:
                log.info("[Monitor] Aircraft with non-matching ICAO Hex Code: %s", sorted(self.icao_code_hex_missing))

            if self.running and self.csv_file:
                self.csv_file.flush()

        log.info("Monitor thread ended.")


    def receive_thr(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            address = (self.dump1090_host, self.dump1090_port)
            s.connect(address)

            log.info("Listening on %s:%s (SBS-1)", self.dump1090_host, self.dump1090_port)

            buffer = ""
            count = 0
            last_time = time.time()
            self.msg_rate_produce = 0

            while self.running:

                try:
                    buffer += s.recv(1024).decode(errors="ignore")
                    lines = buffer.split("\n")
                    buffer = lines[-1]  # keep incomplete line for next recv
                    for line in lines[:-1]:
                        line = line.strip()
                        if not line:
                            continue
                        self.msg_queue.put(line, timeout=2)
                        count += 1
                except queue.Full:
                    pass
                except Exception as e:
                    log.error("Error:", e)

                # Calculate message rate every second
                now = time.time()
                if now - last_time >= 1.0:
                    self.msg_rate_produce = count / (now - last_time)
                    count = 0
                    last_time = now

            log.info("Receive thread ended.")


    def consume(self):

        try:

            count = 0
            last_time = time.time()
            self.msg_rate_consume = 0

            while self.running:

                try:

                    data = self.msg_queue.get(timeout=2)
                    if data:
                        count += 1
                        self.process_sbs_line(data)

                except queue.Empty:
                    pass

                # Calculate message rate every second
                now = time.time()
                if now - last_time >= 1.0:
                    self.msg_rate_consume = count / (now - last_time)
                    count = 0
                    last_time = now

        finally:

            log.info("Closing CSV file.")

            if self.csv_file:
                self.csv_file.close()


    def process_sbs_line(self, line):

        sbs_dict = self.tokenize_fields(line)
        if not sbs_dict:
            return

        log.debug("Received a SBS message.")

        if self.csv_writer:
            self.csv_writer.writerow(sbs_dict)

        ######

        distance_km = self.calculate_distance_to_base(sbs_dict)
        sbs_dict["distance_km"] = distance_km

        if distance_km:
            self.max_observed_distance_km = max(distance_km, self.max_observed_distance_km)

        ######

        self.aggregate_sbs_messages(sbs_dict)

        self.send_to_influx(sbs_dict)

        self.send_alert(sbs_dict)


    def tokenize_fields(self, line):

        if not line.startswith("MSG"):
            return None

        fields = line.split(',')
        if len(fields) < 22:
            return None

        sbs_dict = dict(zip(self.sbs_field_names, fields))
        return sbs_dict


    def calculate_distance_to_base(self, sbs_dict):

        lat = sbs_dict.get("latitude", None)
        lon = sbs_dict.get("longitude", None)

        if not lat or not lon:
            return None

        try:
            lat = float(lat)
            lon = float(lon)
        except Exception:
            return None

        try:
            home_coords = (self.home_lat, self.home_lon)
            distance_km = geodesic(home_coords, (lat, lon)).km
        except Exception:
            return None

        return distance_km

    ###############################################################################

    def aggregate_sbs_messages(self, sbs_dict, ttl_second=30*60):

        hex_ident = sbs_dict.get("hex_ident", None)
        if not hex_ident:
            return

        sbs_dict_clean = {
            k: v for k, v in sbs_dict.items() if v
        }

        key = f"aircraft_aggregate:{hex_ident}"
        self.redis.hset(key, mapping=sbs_dict_clean)
        self.redis.expire(key, ttl_second)

    ###############################################################################

    def send_to_influx(self, sbs_dict):

        hex_ident = sbs_dict.get("hex_ident", None)
        if not hex_ident:
            return

        # find the corresponding aggregate key for this hex_ident
        key = f"aircraft_aggregate:{hex_ident}"
        sbs_dict_aggregate = self.redis.hgetall(key)
        if not sbs_dict_aggregate:
            return

        # TODO

    ###############################################################################

    def send_alert(self, sbs_dict):

        hex_ident = sbs_dict.get("hex_ident", None)
        if not hex_ident:
            return

        distance_km = sbs_dict.get("distance_km", None)
        if not distance_km:
            return

        alert_needed = distance_km <= self.alert_radius_km
        if not alert_needed:
            return

        key_alert = f"alerted:{hex_ident}"
        if self.redis.exists(key_alert):
            return

        # find the corresponding aggregate key for this hex_ident
        key = f"aircraft_aggregate:{hex_ident}"
        sbs_dict_aggregate = self.redis.hgetall(key)
        if not sbs_dict_aggregate:
            return

        callsign = sbs_dict_aggregate.get("callsign", None)
        if not callsign:
            return

        log.info("Sending alert for aircraft %s!", hex_ident)

        self.redis.set(key_alert, 1, ex=600)  # 10 minutes expiration

        self.enrich_sbs_message(sbs_dict_aggregate)

        embed = self.format_sbs_embed(sbs_dict_aggregate)

        status, response = self.discord.send_discord_message(content="✈️ Nearby aircraft detected!", embed=embed)
        if not status:
            log.error(f"Failed to send msg to discord.\n{response}")


    def format_sbs_embed(self, sbs_dict):

        icao_hex = sbs_dict.get("hex_ident") or "Unknown"  # AA8114
        callsign = sbs_dict.get("callsign") or "Unknown"

        latitude = sbs_dict.get("latitude") or "Unknown"   # 37.78368
        longitude = sbs_dict.get("longitude") or "Unknown" # -122.15441
        altitude = sbs_dict.get("altitude") or "Unknown"   # 7950

        ground_speed = sbs_dict.get("ground_speed") or "Unknown"

        distance_km = sbs_dict.get("distance_km")  # 16.653894117511463
        if distance_km:
            distance_km = round(float(distance_km), 2)
        else:
            distance_km = "Unknown"

        enrich_dict = sbs_dict.get("enrich", {})

        registration_number = utility.get_value(enrich_dict, ["airplane", "registration_number"]) or "Unknown" # N776UA
        iata_code_long = utility.get_value(enrich_dict, ["airplane", "iata_code_long"]) or "Unknown"  # B772

        airline_name = utility.get_value(enrich_dict, ["airline", "airline_name"]) or "Unknown"
        country_name = utility.get_value(enrich_dict, ["airline", "country_name"]) or "Unknown"

        thumbnail_url = ""
        img_list = utility.get_value(enrich_dict, ["img"])
        if img_list:
            first_img = img_list[0]
            thumbnail_url = utility.get_value(first_img, ["thumbnail_large", "src"])

        return {
            "title": icao_hex,
            "description": f"Detected {distance_km} km from base at {altitude} ft.",
            "color": 0x1abc9c,  # Teal
            "fields": [
                {
                  "name": "Flight Number",
                  "value": str(callsign),
                  "inline": True
                },
                {
                  "name": "Registration Number",
                  "value": str(registration_number),
                  "inline": True
                },
                {
                  "name": "Aircraft Type",
                  "value": str(iata_code_long),
                  "inline": True
                },
                {
                  "name": "Latitude",
                  "value": str(latitude),
                  "inline": True
                },
                {
                  "name": "Longitude",
                  "value": str(longitude),
                  "inline": True
                },
                {
                  "name": "Ground Speed",
                  "value": str(ground_speed),
                  "inline": True
                },
                {
                  "name": "Airline Name",
                  "value": str(airline_name),
                  "inline": True
                },
                {
                  "name": "Country Name",
                  "value": str(country_name),
                  "inline": True
                }
            ],
            "image": {
                "url": thumbnail_url
            }
        }

    ###############################################################################

    def enrich_sbs_message(self, sbs_dict):

        start_time = time.time()

        sbs_dict["enrich"] = {}

        hex_ident = sbs_dict.get("hex_ident", None)
        sbs_dict["enrich"]["airplane"] = self.enrich_sbs_message_airplane(hex_ident)

        airline_iata = utility.get_value(sbs_dict, ["enrich", "airplane", "airline_iata_code"])
        sbs_dict["enrich"]["airline"] = self.enrich_sbs_message_airline(airline_iata)

        country_iso2 = utility.get_value(sbs_dict, ["enrich", "airline", "country_iso2"])
        sbs_dict["enrich"]["country"] = self.enrich_sbs_message_country(country_iso2)

        sbs_dict["enrich"]["img"] = self.enrich_sbs_message_pic(hex_ident)

        iata_code_long = utility.get_value(sbs_dict, ["enrich", "airplane", "iata_code_long"])
        sbs_dict["enrich"]["svg"] = self.enrich_sbs_message_svg(iata_code_long)

        duration = time.time() - start_time
        elapsed = utility.elapsed_format(duration)
        log.debug("Enriching SBS message completed in %s", elapsed)


    def enrich_sbs_message_airplane(self, hex_ident):

        if not hex_ident:
            log.warning("hex_ident is missing for this SBS message")
            return None

        hex_ident = hex_ident.strip().upper()

        results = self.postgresql_session.query(models_sql.Airplane).filter_by(icao_code_hex=hex_ident).all()
        if results:
            if len(results) > 1:
                log.warning("Multiple airplanes found with hex_ident %s", hex_ident)
            return models_sql.model_to_dict(results[0])

        status, output = self.hexdb.get_aircraft_information(hex_ident)

        if status:

            output["icao_code_hex"] = output.pop("ModeS")
            output["registration_number"] = output.pop("Registration")
            # output["?"] = output.pop("Manufacturer")  # Airbus
            output["iata_code_long"] = output.pop("ICAOTypeCode")
            output["iata_type"] = output.pop("Type")    # 'A319 111', 'Global 5000'
            output["plane_owner"] = output.pop("RegisteredOwners")  # easyJet UK
            # output["?"] = output.pop("OperatorFlagCode")          # EZY

            return output

        else:

            log.debug("get_aircraft_information failed: %s", output)

        self.icao_code_hex_missing.add(hex_ident)
        return None


    def enrich_sbs_message_airline(self, airline_iata):

        if not airline_iata:
            return None

        airline_iata = airline_iata.strip().upper()
        results = self.postgresql_session.query(models_sql.Airline).filter_by(iata_code=airline_iata, status="active").all()
        if not results:
            return None

        if len(results) > 1:
            log.warning("Multiple active airlines found with airline_iata %s", airline_iata)

        return models_sql.model_to_dict(results[0])


    def enrich_sbs_message_country(self, country_iso2):

        if not country_iso2:
            return None

        country_iso2 = country_iso2.strip().upper()
        results = self.postgresql_session.query(models_sql.Country).filter_by(country_iso2=country_iso2).all()
        if not results:
            return None

        if len(results) > 1:
            log.warning("Multiple countries found with country_iso2 %s", country_iso2)

        return models_sql.model_to_dict(results[0])


    def enrich_sbs_message_pic(self, hex_ident):

        status, output = self.ps_h.get_aircraft_picture(hex_ident)
        if not status:
            log.warning("enrich_sbs_message_pic failed: %s", output)
            return None

        return output


    def enrich_sbs_message_svg(self, iata_code_long):

        if not iata_code_long:
            return None

        iata_code_long = iata_code_long.strip().upper()
        results = self.postgresql_session.query(models_sql.ICAOType).filter_by(designator=iata_code_long).all()
        if not results:
            return None

        output = models_sql.model_to_dict(results[0])

        designator = output.get("designator", None)
        description_code = output.get("description_code", None)
        description = output.get("aircraft_description", None)
        wtc = output.get("wake_turbulence_category", None)

        svg = get_aircraft_svg.get_base_marker(designator,         # B737
                                               description_code,   # L2J
                                               description,        # LandPlane
                                               wtc)                # M

        return svg

    ###############################################################################

sw_h = None

def handle_sigint(signum, frame):

    log.info("\n[!] Caught Ctrl+C. Exiting gracefully.")

    if sw_h:
        sw_h.stop()

    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

gc.collect()

models_sql.init_db()

sw_h = SkyWatch(csv_save=False, alert_radius_km=3)
sw_h.start()
