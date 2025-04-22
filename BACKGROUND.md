## ADS-B

ADS-B (Automatic Dependent Surveillance–Broadcast) is a surveillance technology used in aviation that allows aircraft to automatically broadcast their position, velocity, altitude, and other flight data to air traffic control and nearby aircraft. It relies on GPS for precise positioning (automatic), data is sent without being requested (dependent), and it is broadcast continuously via radio signals.

ADS-B enhances situational awareness, reduces the need for radar, and supports more efficient air traffic management. It plays a crucial role in modern airspace systems, enabling features like real-time tracking, improved safety, and separation in both controlled and uncontrolled airspace.

## ADS-B Frequencies

1090 MHz and 978 MHz are two frequencies used for ADS-B, and they serve different purposes and aircraft types.

- `1090 MHz` (Mode S / ES) is the global standard used by commercial airliners, business jets, and most transponder-equipped aircraft, transmitting extended squitter messages received by radar and ADS-B ground stations worldwide.

- `978 MHz` (UAT - Universal Access Transceiver) is only used in the United States, primarily by General Aviation (GA) aircraft flying below 18,000 feet, offering additional weather and traffic data services through the FAA.

While 1090 MHz is required for high-altitude or international flights, 978 MHz provides a lower-cost option with added benefits for U.S.-based GA pilots.

## ADS-B Receivers

Devices that receive ADS-B data are commonly referred to as ADS-B receivers.

These include a range of hardware types such as:

- USB SDR dongles  (e.g., FlightAware Pro Stick, RTL-SDR)
- Standalone receivers (e.g., RadarBox XRange series)
- Integrated avionics systems onboard aircraft

On the ground, these receivers capture ADS-B transmissions broadcast by aircraft on either 1090 MHz or 978 MHz, then decode the data using software for visualization, logging, or relaying to flight tracking networks like FlightAware or RadarBox. Some high-end receivers may include built-in GPS, filtering, and networking capabilities for precise timekeeping and multi-lateration (MLAT) support.

## USB Software-Defined Radio (SDR) Dongles

Here are well-known USB SDR dongles, which function as radio receivers capable of decoding ADS-B signals:

| Feature / Model              | Pro Stick (1090) | Pro Stick Plus (1090)  | Pro Stick 978        | RB FlightStick (1090)  | RB FlightStick (978) |
|------------------------------|------------------|------------------------|----------------------|------------------------|----------------------|
| **Company**                  | FlightAware      | FlightAware            | FlightAware          | AirNav Systems         | AirNav Systems       |
| **Year Introduced**          | ~2016            | ~2017                  | ~2018                | ~2019                  | ~2020                |
| **Primary Frequency**        | 1090 MHz         | 1090 MHz               | 978 MHz              | 1090 MHz               | 978 MHz              |
| **Built-in Amplifier (LNA)** | Yes              | Yes                    | Yes                  | Yes                    | Yes                  |
| **Bandpass Filter**          | `No`             | Yes                    | Yes                  | Yes                    | Yes                  |
| **TCXO (Low-drift)**         | 0.5 ppm          | 0.5 ppm                | 0.5 ppm              | Yes                    | Yes                  |
| **Bias-T Power Supply**      | `No`             | `No`                   | `No`                 | Yes                    | Yes                  |
| **ESD Protection**           | `No`             | `No`                   | `No`                 | Yes                    | Yes                  |
| **MLAT Support**             | Yes              | Yes                    | `No`                 | Yes                    | `No`                 |

These dongles do not operate independently; they require connection to a host system, such as a Raspberry Pi, desktop, or laptop, to process the incoming data. The host runs the necessary software to decode, visualize, and optionally feed the data to flight tracking networks.

All USB SDR dongles above are based on the Realtek `RTL2832U` chipset. It is a low-cost USB demodulator chip originally designed for receiving digital TV signals (DVB-T) on a computer. What makes it unique and widely popular in the SDR community is its ability to expose raw I/Q (in-phase and quadrature) data from the tuner when paired with compatible RF front-ends like the Rafael Micro R820T. This capability allows the chip to be repurposed for a wide range of radio frequency applications beyond TV, such as listening to FM radio, decoding weather satellite images, receiving ADS-B aircraft signals, and more—transforming it into an affordable SDR platform for both hobbyists and researchers.

Two major companies that manufacture and sell ADS-B receivers, especially for hobbyist and enthusiast use:

- FlightAware is a leading aviation data company headquartered in Houston, Texas, USA. It provides PiAware, an open-source software suite designed for Raspberry Pi devices, enabling the reception, decoding, and sharing of ADS-B data. FlightAware operates a global network of over 37,000 ADS-B ground stations, significantly enhancing real-time flight tracking coverage across the world.

- AirNav Systems, based in Tampa, Florida, USA, is the company behind RadarBox, a comprehensive flight tracking platform that integrates data from ADS-B receivers, satellite feeds, FAA data, and other aviation sources. The company maintains a network of over 29,000 ADS-B feeders worldwide, supporting its extensive and accurate global flight tracking infrastructure.

## dump1090

dump1090 is an open-source Mode S decoder specifically designed to work with RTL-SDR USB receivers to capture and decode ADS-B signals broadcast by aircraft. It receives data on the 1090 MHz frequency, extracting real-time information such as aircraft position, altitude, speed, and identification.

The repository [antirez/dump1090](https://github.com/antirez/dump1090) was the original implementation of dump1090, created by Salvatore Sanfilippo, better known as antirez — the same developer who created the Redis in-memory database. It was created around 2013 as a quick-and-efficient way to decode ADS-B signals from aircraft using the then-new RTL-SDR dongles. It was written in C and focused on speed and simplicity. This repository is no longer maintained.

Although `antirez/dump1090` was minimal and barebones, it sparked the interest of hobbyists and developers. This led to multiple community forks that added features like:

- Interactive web-based maps (SkyAware)
- Networking for feeding data to aggregation services (FlightAware, FR24)
- Better support for filtering, gain control, and aircraft state tracking

There are multiple forks of `antirez/dump1090`, but FlightAware's [fork](https://github.com/flightaware/dump1090) is actively maintained and widely used today.

## ADS-B Data Feeder

An ADS-B data feeder is a software service or tool that collects real-time aircraft position data—broadcast via ADS-B signals—from a local receiver (usually an RTL-SDR dongle running with software like dump1090) and transmits it to an aviation tracking network such as FlightAware, Flightradar24, or RadarBox. These feeders enable global flight tracking services to aggregate data from thousands of volunteer-operated receivers worldwide, enhancing their coverage, accuracy, and visibility of aircraft even in remote areas. Feeder software often includes tools for decoding, formatting, and securely uploading the data, and many networks offer benefits to contributors, such as free premium access.

| Feeder Software            | Primary Network(s)         | Description                                                                                                                  |
|----------------------------|----------------------------|------------------------------------------------------------------------------------------------------------------------------|
| **PiAware**                | FlightAware                | Official feeder for FlightAware; includes `dump1090-fa` and SkyAware UI. Highly popular for its ease of use and integration. |
| **FR24 Feeder**            | Flightradar24              | Feeds data to Flightradar24; supports RTL-SDR or external sources like `dump1090`. Easy to install and configure.            |
| **RBFeeder**               | RadarBox (AirNav Systems)  | Feeds ADS-B data to RadarBox; supports both 1090 MHz and 978 MHz. Offers filtering and status dashboard.                     |
| **ADS-B Exchange Feeder**  | ADS-B Exchange             | Sends unfiltered ADS-B data to ADS-B Exchange. Preferred by enthusiasts seeking open tracking.                               |
| **OpenSky Feeder**         | OpenSky Network            | Research-focused network with strict data quality; less popular but valuable for academic use.                               |

## Aircraft Tracking Terminologies

Aircraft tracking terminologies refer to the standardized set of data fields and identifiers used to monitor and interpret aircraft movements via systems like ADS-B, Mode S, and radar. Together, these fields provide a real-time snapshot of an aircraft’s identity, status, and behavior in the sky, forming the foundation of air traffic control systems and flight tracking services.

- ICAO 24-bit Address (Mode S, Hex Code)

    The ICAO 24-bit address, also known as the Mode S address or hex code, is a globally unique identifier assigned to every aircraft transponder by the national aviation authority (e.g., the FAA in the U.S.). It is represented as a 6-digit hexadecimal value (e.g., A68631) and is used in surveillance systems like ADS-B and Mode S radar to track and identify aircraft. Unlike a registration number or callsign, which can change, the ICAO hex code is typically fixed for the lifetime of the transponder.

- ICAO Type Code (ICAO aircraft type designator)

    This is a standardized 4-character alphanumeric identifier defined by the International Civil Aviation Organization (ICAO) to represent a specific aircraft model. It is used globally in flight plans, tracking systems, and aviation databases. For example, `A319` refers to the Airbus A319, and `B738` refers to the Boeing 737-800. This code enables air traffic controllers and systems to quickly recognize the aircraft’s performance class, weight category, and operational characteristics, which are crucial for airspace management and separation requirements.

    These codes are officially cataloged in `ICAO Document 8643: Aircraft Type Designators`, which serves as the global reference for aircraft type classification. You can access the document in [here](https://www.icao.int/publications/doc8643/pages/search.aspx).

- Operator Flag Code (ICAO airline designator)

    The Operator Flag Code, often known as the ICAO airline designator, is a three-letter code assigned by ICAO to commercial air operators. It is used in flight tracking and ATC systems to identify the airline operating the aircraft. For example, `EZY` represents easyJet, and `UAL` represents United Airlines. This code appears alongside the flight number in the callsign (e.g., EZY123) and is essential for identifying the airline responsible for a given flight, especially when aircraft are shared, leased, or repainted.

- Registration

    An aircraft's registration is its unique alphanumeric tail number, similar to a car license plate, assigned by the national aviation authority in the country where the aircraft is registered. For example, `N5197F` is a U.S.-registered aircraft, while `G-EZBZ` is registered in the United Kingdom. The registration typically appears on the aircraft’s fuselage and is used for legal identification, ownership verification, and regulatory compliance. In ADS-B systems, registration helps link transponder data to publicly accessible aircraft records.

- Callsign (the flight's public identifier)

    A callsign is the flight identifier used for radio communication between an aircraft and air traffic control (ATC). It often represents the airline and flight number (e.g., `UAL123` for United Airlines Flight 123), but in the case of general aviation, it may be the aircraft's registration number (e.g., N5197F). Callsigns are broadcast in ADS-B messages and appear in flight tracking systems, helping distinguish flights even if multiple aircraft are nearby.

- Squawk Code

    A squawk code is a four-digit transponder code assigned by air traffic control (ATC) that identifies the aircraft on radar. It is set manually by the pilot and can convey special conditions — for example, `7500` indicates hijacking, `7600` indicates radio failure, and `7700` signals a general emergency. Most flights use random codes like `1200` for VFR (visual flight rules) in the U.S. or a unique code for tracking under radar surveillance.

- Latitude / Longitude / Altitude

    Latitude and longitude represent the aircraft’s location on Earth’s surface using geographic coordinates (e.g., 37.926°, -122.070°), while altitude indicates its height above mean sea level, typically in feet. These three parameters define the aircraft’s current 3D position in space. Together, they allow for precise tracking of aircraft positions, enabling services like Flightradar24 and ADS-B Exchange to render aircraft in real time on maps.

- Ground Speed

    Ground speed refers to the actual horizontal speed of the aircraft relative to the ground, measured in knots (nautical miles per hour). Ground speed is crucial for navigation and flight tracking, as it indicates how fast the aircraft is moving over the Earth's surface — a value affected by wind and direction of flight.

- Airspeed

    Airspeed is the speed of an aircraft relative to the surrounding air through which it is moving. Unlike ground speed, which measures how fast the aircraft travels over the Earth's surface, airspeed reflects how fast the aircraft is moving through the air mass and is crucial for flight performance, control, and safety. There are several types of airspeed:

    - **Indicated Airspeed (IAS)**: The airspeed directly read from the aircraft's airspeed indicator, without correction for instrument or position errors. Used by pilots for most flight operations.

    - **Calibrated Airspeed (CAS)**: IAS corrected for position and instrument errors. More accurate than IAS, especially at low speeds and during maneuvers.

    - **Equivalent Airspeed (EAS)**: CAS corrected for compressibility effects at higher speeds. Used in performance calculations for high-speed aircraft.

    - **True Airspeed (TAS)**: EAS corrected for air density (altitude and temperature). Represents the actual speed through the air mass. Important for navigation and flight planning.

    Airspeed is essential for managing takeoff, climb, cruise, descent, and landing phases safely and efficiently.

- Vertical Rate

    Vertical rate, also called climb/descent rate, measures how quickly the aircraft is gaining or losing altitude, typically expressed in feet per minute (fpm). A positive vertical rate indicates a `climb`, while a negative rate indicates `descent`. This parameter helps determine flight phases (e.g., ascent, descent, level flight) and is important for air traffic controllers and flight safety systems.

- Heading

    Heading is the direction in which the nose of the aircraft is pointed, measured in degrees from true or magnetic north (0° to 359°). It represents the aircraft’s orientation, not necessarily its actual movement over the ground. Pilots use heading to steer the aircraft, often adjusting for wind correction angles to stay on course. For instance, if strong winds are pushing the aircraft sideways, the pilot may point the nose slightly into the wind to maintain a desired ground track. Heading is typically shown on cockpit instruments like the heading indicator or compass.

- Track (ground track)

    Track (also called ground track) is the actual path the aircraft is following over the ground, measured in degrees from true north. It represents the direction of movement based on the aircraft’s position change over time and accounts for wind drift. Unlike heading, which shows where the nose is pointing, track shows where the aircraft is truly going. For example, an aircraft might have a heading of 090° (due east) but a track of 080° if a wind is blowing it slightly southward.

## SBS-1 BaseStation Format

The SBS-1 BaseStation format is a plain-text line-based protocol developed by Kinetic for its SBS-1 ADS-B receivers. It is widely used by software like dump1090-fa to output live aircraft data over TCP (commonly port 30003). Each line represents a single message and contains 22 comma-separated fields.

| Field # | Field Name         | Description                                                      |
|--------:|--------------------|------------------------------------------------------------------|
| 0       | `MessageType`      | Always `"MSG"` for ADS-B messages.                               |
| 1       | `TransmissionType` | Subtype (1–8), indicating the kind of data (check next table)    |
| 2       | `SessionID`        | Internal session ID (can be ignored).                            |
| 3       | `AircraftID`       | Internal aircraft ID (can be ignored).                           |
| 4       | `HexIdent`         | ICAO 24-bit hex code (e.g. `A68631`).                            |
| 5       | `FlightID`         | Internal flight ID (can be ignored).                             |
| 6       | `DateGenerated`    | Date when the message was generated (UTC).                       |
| 7       | `TimeGenerated`    | Time when the message was generated (UTC).                       |
| 8       | `DateLogged`       | Date when the message was logged (UTC).                          |
| 9       | `TimeLogged`       | Time when the message was logged (UTC).                          |
| 10      | `Callsign`         | Flight callsign (e.g., `UAL123`).                                |
| 11      | `Altitude`         | Altitude in feet.                                                |
| 12      | `GroundSpeed`      | Speed over ground in knots.                                      |
| 13      | `Track`            | Degrees clockwise from true north.                               |
| 14      | `Latitude`         | Aircraft latitude.                                               |
| 15      | `Longitude`        | Aircraft longitude.                                              |
| 16      | `VerticalRate`     | Climb/descent rate in feet per minute.                           |
| 17      | `Squawk`           | Assigned transponder squawk code.                                |
| 18      | `Alert`            | Alert flag (1 = squawk change).                                  |
| 19      | `Emergency`        | Emergency flag (1 = emergency).                                  |
| 20      | `SPI`              | Special Position Identification flag (1 = SPI set).              |
| 21      | `IsOnGround`       | Ground flag (`1`=on ground, `0`=airborne).                       |

Transmission types are:

| Subtype | Name                                           | Description                                                 |
|---------|------------------------------------------------|-------------------------------------------------------------|
| 1       | **ES Identification and Category**             | Aircraft ID and category (e.g., callsign and type)          |
| 2       | **ES Surface Position**                        | Position on the ground (taxiing, ground speed, etc.)        |
| 3       | **ES Airborne Position (Barometric Altitude)** | Position in the air (lat/lon, barometric altitude)          |
| 4       | **ES Airborne Velocity**                       | Airborne speed, heading, and vertical rate                  |
| 5       | **Surveillance Altitude**                      | Position from Mode S (non-ADS-B) — includes altitude        |
| 6       | **Surveillance ID**                            | Identifies the aircraft with a squawk code from Mode S      |
| 7       | **Airlift or Emergency**                       | Emergency, SPI (Ident), alert, or other special condition   |
| 8       | **ES Aircraft Status / Extended Squitter**     | Typically includes aircraft status or ADS-B version         |

SBS-1 BaseStation format is ideal for developers and hobbyists because it requires no binary decoding and is compatible with many tools, including Virtual Radar Server, PlanePlotter, and custom scripts. By connecting to port 30003, applications can ingest real-time aircraft telemetry without needing to parse raw Mode S or Beast-format messages.

The SBS-1 BaseStation format includes many essential parameters directly transmitted by aircraft. However, not all relevant flight data is present in this format. Parameters like the aircraft's ICAO type code, registration number, and operator flag code are not included in SBS messages and must be obtained through external databases or aviation APIs using the ICAO hex code as a lookup key. Similarly, high-level flight information such as departure and arrival airports, scheduled and estimated times, and route details are absent and must be inferred or retrieved via services like FlightAware, OpenSky Network, or ADS-B Exchange. While SBS-1 provides the foundational raw data, full flight context often requires enrichment from third-party sources.

| **Parameter**           | **How to Obtain**                                                                                       |
|-------------------------|---------------------------------------------------------------------------------------------------------|
| **ICAO Type Code**      | Use external databases like `ICAO 8643`, `FAA`, or `OpenSky` using the ICAO hex code or registration.   |
| **Operator Flag Code**  | Enrich via lookup APIs such as `OpenSky`, `PlaneBase`, or `ADS-B Exchange`.                             |
| **Registration**        | Resolve using the ICAO hex code from public aircraft registries or aviation APIs.                       |
| **Airspeed**            | Cannot be reliably extracted; may be estimated using ground speed and vertical rate, but not accurate.  |
| **Heading**             | Not explicitly transmitted; not derivable from SBS messages alone.                                      |
| **Flight Information**  | Retrieve from APIs like `FlightAware`, `OpenSky`, or `FlightRadar24` based on callsign or ICAO hex.     |
