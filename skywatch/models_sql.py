
# Author: Mani Amoozadeh
# Email: mani.amoozadeh2@gmail.com
# Description: model for interacting with Postgresql

import os
import json
import logging
import time
import csv
import gc
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, Date
from sqlalchemy import inspect

import utility

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

DATABASE_URL = "postgresql://admin:admin123@localhost:5432/flight"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class AircraftType(Base):
    __tablename__ = 'aircraft_types'

    id = Column(String, primary_key=True)  # 22292
    iata_code = Column(String)             # 73N
    aircraft_name = Column(String)         # Boeing 737-300 Mixed Config
    plane_type_id = Column(String)         # 65


class Airline(Base):
    __tablename__ = 'airlines'

    id = Column(String, primary_key=True)     # "4441699"
    fleet_average_age = Column(String)
    airline_id = Column(String)               # 1966
    callsign = Column(String)                 # null
    hub_code = Column(String)                 # LAX
    iata_code = Column(String)                # GM
    icao_code = Column(String)                # AMR
    country_iso2 = Column(String)             # US
    date_founded = Column(String)
    iata_prefix_accounting = Column(String)
    airline_name = Column(String)             # "Air America"
    country_name = Column(String)             # "United States"
    fleet_size = Column(String)
    status = Column(String)                   # "disabled"
    type = Column(String)                     # "charter"

# | **Airline Status**         | **Description**                                                                 |
# |----------------------------|---------------------------------------------------------------------------------|
# | `active`                   | Currently operating and serving flights.                                        |
# | `disabled`                 | Airline profile is inactive or intentionally hidden (may not operate flights).  |
# | `historical`               | Airline that no longer operates; preserved for record/history.                  |
# | `historical/administration`| Airline has ceased ops and is in administrative or legal wind-down phase.       |
# | `merged`                   | Airline merged into another (e.g., US Airways into American).                   |
# | `not_ready`                | Incomplete entry, possibly a placeholder or pending validation.                 |
# | `renamed`                  | Airline has changed name — consider linking to the current one.                 |
# | `restarting`               | Airline is planning to resume operations but not yet active.                    |
# | `start_up`                 | Airline planning to launch; not operational yet.                                |
# | `unknown`                  | Status not determined or missing.                                               |

class Airplane(Base):
    __tablename__ = 'airplanes'

    id = Column(String, primary_key=True)      # "6454111"
    iata_type = Column(String)                 # "B737-300"
    airplane_id = Column(String)               # "1"
    airline_iata_code = Column(String)         # "0B"
    iata_code_long = Column(String)            # "B733"
    iata_code_short = Column(String)           # "733"
    airline_icao_code = Column(String)         # null
    construction_number = Column(String)       # "23653"
    delivery_date = Column(Date)               # "1986-08-21T22:00:00.000Z"
    engines_count = Column(String)             # "2"
    engines_type = Column(String)              # "JET"
    first_flight_date = Column(Date)           # "1986-08-02T22:00:00.000Z"
    icao_code_hex = Column(String)             # "4A0823"
    line_number = Column(String)               # "1260"
    model_code = Column(String)                # "B737-377"
    registration_number = Column(String)       # "YR-BAC"
    test_registration_number = Column(String)  # null
    plane_age = Column(String)                 # "31"
    plane_class = Column(String)               # null
    model_name = Column(String)                # "737"
    plane_owner = Column(String)               # "Airwork Flight Operations Ltd"
    plane_series = Column(String)              # "377"
    plane_status = Column(String)              # "active"
    production_line = Column(String)           # "Boeing 737 Classic"
    registration_date = Column(String)         # "0000-00-00"
    rollout_date = Column(String)              # null


class Airport(Base):
    __tablename__ = 'airports'

    id = Column(String, primary_key=True)  # "3487527"
    gmt = Column(String)                   # "-10"
    airport_id = Column(String)            # "1"
    iata_code = Column(String)             # "AAA"
    city_iata_code = Column(String)        # "AAA"
    icao_code = Column(String)             # "NTGA"
    country_iso2 = Column(String)          # "PF"
    geoname_id = Column(String)            # "6947726"
    latitude = Column(String)              # "-17.05"
    longitude = Column(String)             # "-145.41667"
    airport_name = Column(String)          # "Anaa"
    country_name = Column(String)          # "French Polynesia"
    phone_number = Column(String)          # null
    timezone = Column(String)              # "Pacific/Tahiti"


class City(Base):
    __tablename__ = 'cities'

    id = Column(String, primary_key=True)  # "3158184"
    gmt = Column(String)                   # "-8"
    city_id = Column(String)               # "238"
    iata_code = Column(String)             # "ALW"
    country_iso2 = Column(String)          # "US"
    geoname_id = Column(String)            # "5814916"
    latitude = Column(String)              # "46.094723"
    longitude = Column(String)             # "-118.291115"
    city_name = Column(String)             # "Walla Walla"
    timezone = Column(String)              # "America/Los_Angeles"


class Country(Base):
    __tablename__ = 'countries'

    id = Column(String, primary_key=True)  # "83743"
    capital = Column(String)               # "London"
    currency_code = Column(String)         # "GBP"
    fips_code = Column(String)             # "UK"
    country_iso2 = Column(String)          # "GB"
    country_iso3 = Column(String)          # "GBR"
    continent = Column(String)             # "EU"
    country_id = Column(String)            # "79"
    country_name = Column(String)          # "United Kingdom"
    currency_name = Column(String)         # "Pound"
    country_iso_numeric = Column(String)   # "826"
    phone_prefix = Column(String)          # "44"
    population = Column(String)            # "62348447"


class ICAOType(Base):
    __tablename__ = 'icao_doc8643_2019'

    id = Column(Integer, primary_key=True, autoincrement=True)
    aircraft_description = Column(String)  # e.g. "LandPlane"
    description_code = Column(String)      # e.g. "L2J"
    designator = Column(String)            # e.g. "J328"
    engine_count = Column(String)
    engine_type = Column(String)
    manufacturer_code = Column(String)
    model_full_name = Column(String)
    wake_turbulence_category = Column(String)  # "L", "M", etc.


class FAAAircraft(Base):
    __tablename__ = 'faa_2018'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_completed = Column(String)  # e.g. "2018-7月-3"
    manufacturer = Column(String)  # e.g. "Acro Sport"
    model = Column(String)  # e.g. "Acro Sport II"
    physical_class = Column(String)  # "Piston", "Jet", etc.
    engine_count = Column(String)  # "# Engines"
    aac = Column(String)  # "A"
    adg = Column(String)  # "I"
    tdg = Column(String)  # "1A"
    approach_speed_vref = Column(String)  # e.g. "56"
    wingtip_configuration = Column(String)  # "no winglets"
    wingspan_ft = Column(String)
    length_ft = Column(String)
    tail_height_ft = Column(String)
    wheelbase_ft = Column(String)
    cockpit_to_main_gear = Column(String)
    mgw_outer_to_outer = Column(String)
    mtow = Column(String)
    max_ramp_max_taxi = Column(String)
    main_gear_config = Column(String)  # "S"
    icao_code = Column(String)
    wake_category = Column(String)
    atct_weight_class = Column(String)
    years_manufactured = Column(String)
    note = Column(String)
    parking_area_sf = Column(String)


class SBSMessage(Base):
    __tablename__ = 'sbs_messages'

    id = Column(Integer, primary_key=True)
    hex_ident = Column(String)
    msg_type = Column(Integer)
    transmission_type = Column(Integer)
    session_id = Column(String)
    aircraft_id = Column(String)
    flight_id = Column(String)
    generated_datetime = Column(DateTime)
    logged_datetime = Column(DateTime)
    callsign = Column(String)
    altitude = Column(Integer)
    ground_speed = Column(Float)
    track = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    vertical_rate = Column(Integer)
    squawk = Column(String)
    alert = Column(Boolean)
    emergency = Column(Boolean)
    spi = Column(Boolean)
    is_on_ground = Column(Boolean)


def init_db():

    Base.metadata.create_all(engine)
    load_json_to_db()
    load_csv_to_db()


def load_json_to_db():

    start_time = time.time()

    load_json_to_model("db/aircraft_types.json", AircraftType)
    load_json_to_model("db/airlines.json", Airline)
    load_json_to_model("db/airplanes.json", Airplane, date_fields=["delivery_date", "first_flight_date"])
    load_json_to_model("db/airports.json", Airport)
    load_json_to_model("db/cities.json", City)
    load_json_to_model("db/countries.json", Country)

    duration = time.time() - start_time
    elapsed = utility.elapsed_format(duration)
    log.info("JSON import completed in %s", elapsed)

    gc.collect()


def load_json_to_model(filepath, model, date_fields=None):

    session = Session(bind=engine)
    inspector = inspect(engine)

    has_table = inspector.has_table(model.__tablename__)
    entry_count = session.query(model).count()

    if has_table and entry_count != 0:
        return

    if not os.path.exists(filepath):
        log.warning("%s does not exist.", filepath)
        return

    log.info("Loading %s...", model.__tablename__)

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:

        if date_fields:

            for field in date_fields:
                value = item.get(field)
                if value and value != "0000-00-00":
                    try:
                        item[field] = datetime.fromisoformat(value).date()
                    except ValueError:
                        item[field] = None
                else:
                    item[field] = None

        session.merge(model(**item))

    session.commit()

    log.info("Loaded %s records into %s.", len(data), model.__tablename__)


def load_csv_to_db():

    start_time = time.time()

    load_csv_to_model("db/ICAO-doc8643-2019.csv", ICAOType)
    load_csv_to_model("db/FAA-201810.csv", FAAAircraft)

    duration = time.time() - start_time
    elapsed = utility.elapsed_format(duration)
    log.info("CSV import completed in %s", elapsed)

    gc.collect()


def load_csv_to_model(filepath, model):

    session = Session(bind=engine)
    inspector = inspect(engine)

    has_table = inspector.has_table(model.__tablename__)
    entry_count = session.query(model).count()

    if has_table and entry_count != 0:
        return

    if not os.path.exists(filepath):
        log.warning("%s does not exist.", filepath)
        return

    log.info("Loading %s...", model.__tablename__)

    with open(filepath, newline='', encoding='utf-8') as csvfile:

        reader = csv.DictReader(csvfile)

        count = 0
        for row in reader:
            session.add(model(**row))
            count += 1

        session.commit()

        log.info("Loaded %s records into %s.", count, model.__tablename__)


def model_to_dict(obj, fields=None):

    return {
        column.name: getattr(obj, column.name)
        for column in obj.__table__.columns
        if not fields or column.name in fields
    }
