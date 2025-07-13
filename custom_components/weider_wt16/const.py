"""Constants for the Weider WT16 Heat Pump integration."""

DOMAIN = "weider_wt16"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_MODBUS_ADDR = "modbus_addr"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_CREATE_DASHBOARD = "create_dashboard"

DEFAULT_PORT = 502
DEFAULT_MODBUS_ADDR = 1
DEFAULT_SCAN_INTERVAL = 60

DEVICE_INFO = {
    "identifiers": {(DOMAIN, "weider_wt16_heatpump")},
    "name": "Weider WT16 Heat Pump",
    "manufacturer": "Weider",
    "model": "WT16",
}

# Dashboard view configuration for adding to existing dashboard
DASHBOARD_VIEW_CONFIG = {
    "title": "Wärmepumpe",
    "path": "warmepumpe",
    "type": "sections",
    "sections": [
        {
            "title": "Temperatur Regelung",
            "type": "grid",
            "cards": [
                {"type": "thermostat", "entity": "climate.raum_soll_temperatur", "name": "Raumtemperatur"},
                {"type": "thermostat", "entity": "climate.warmwasser_temperatur", "name": "Warmwasser"},
            ],
        },
        {
            "title": "Temperatur Verlauf",
            "type": "grid",
            "cards": [
                {
                    "type": "history-graph",
                    "title": "Temperatur Übersicht",
                    "hours_to_show": 24,
                    "refresh_interval": 60,
                    "entities": [
                        "sensor.warmwasser_ist_temperatur",
                        "sensor.puffer_ist_temperatur",
                        "sensor.wp1_vorlauf_ist_temperatur",
                        "sensor.vorlauf_soll_temperatur",
                        "sensor.aussentemperatur",
                    ],
                }
            ],
        },
        {
            "title": "System Status",
            "type": "grid",
            "cards": [
                {
                    "type": "entities",
                    "title": "Betriebszustände",
                    "entities": [
                        {"entity": "binary_sensor.verdichter_wp1", "name": "Verdichter WP1", "icon": "mdi:engine"},
                        {"entity": "binary_sensor.up_warmwasser", "name": "UP-Warmwasser", "icon": "mdi:pump"},
                        {"entity": "binary_sensor.up_heizen_wp1", "name": "UP-Heizen WP1", "icon": "mdi:pump"},
                        {"entity": "binary_sensor.up_sole_wasser_wp1", "name": "UP-Sole/Wasser WP1", "icon": "mdi:pump"},
                        {"entity": "binary_sensor.up_mischer_1", "name": "UP-Mischer 1", "icon": "mdi:pump"},
                        {"entity": "binary_sensor.stromungswachter_wp1", "name": "Strömungswächter WP1", "icon": "mdi:water-pump"},
                    ],
                },
                {
                    "type": "entities",
                    "title": "Störungen & Sperren",
                    "entities": [
                        {"entity": "binary_sensor.fernstorung", "name": "Fernstörung", "icon": "mdi:alert-circle"},
                        {"entity": "binary_sensor.sperre_warmwasser", "name": "Sperre Warmwasser", "icon": "mdi:lock"},
                        {"entity": "binary_sensor.sperre_heizen", "name": "Sperre Heizen", "icon": "mdi:lock"},
                        {"entity": "binary_sensor.evu_sperre", "name": "EVU-Sperre", "icon": "mdi:transmission-tower"},
                        {"entity": "binary_sensor.sgready_1", "name": "SGready 1", "icon": "mdi:flash"},
                        {"entity": "binary_sensor.sgready_2", "name": "SGready 2", "icon": "mdi:flash"},
                    ],
                },
                {
                    "type": "entities",
                    "title": "Fehlermeldungen",
                    "entities": [
                        {"entity": "sensor.aktive_fehlermeldung", "name": "Aktive Fehlermeldung", "icon": "mdi:alert-circle-outline"},
                    ],
                },
            ],
        },
        {
            "title": "Temperaturen",
            "type": "grid",
            "cards": [
                {
                    "type": "entities",
                    "title": "Wichtige Temperaturen",
                    "entities": [
                        {"entity": "sensor.aussentemperatur", "name": "Außentemperatur", "icon": "mdi:thermometer"},
                        {"entity": "sensor.warmwasser_ist_temperatur", "name": "Warmwasser Ist-Temperatur", "icon": "mdi:water-thermometer"},
                        {"entity": "sensor.raum_ist_temperatur", "name": "Raum Ist-Temperatur", "icon": "mdi:home-thermometer"},
                        {"entity": "sensor.wp1_vorlauf_ist_temperatur", "name": "WP1 Vorlauf Ist-Temperatur", "icon": "mdi:thermometer-lines"},
                        {"entity": "sensor.wp1_rucklauf_ist_temperatur", "name": "WP1 Rücklauf Ist-Temperatur", "icon": "mdi:thermometer-lines"},
                        {"entity": "sensor.puffer_ist_temperatur", "name": "Puffer Ist-Temperatur", "icon": "mdi:storage-tank"},
                    ],
                },
                {
                    "type": "entities",
                    "title": "WP1 Temperaturen",
                    "entities": [
                        {"entity": "sensor.wp1_verdampfungstemperatur", "name": "Verdampfungstemperatur"},
                        {"entity": "sensor.wp1_verflussigungstemperatur", "name": "Verflüssigungstemperatur"},
                        {"entity": "sensor.wp1_uberhitzung", "name": "Überhitzung"},
                        {"entity": "sensor.wp1_heissgas_temperatur", "name": "Heißgas Temperatur"},
                        {"entity": "sensor.wp1_sauggas_temperatur", "name": "Sauggas Temperatur"},
                        {"entity": "sensor.wp1_verdampfer_temperatur", "name": "Verdampfer Temperatur"},
                        {"entity": "sensor.wp1_quelle_eintritt_temperatur", "name": "Quelle Eintritt"},
                        {"entity": "sensor.wp1_quelle_austritt_temperatur", "name": "Quelle Austritt"},
                    ],
                },
            ],
        },
        {
            "title": "EVI System",
            "type": "grid",
            "cards": [
                {
                    "type": "entities",
                    "title": "EVI Temperaturen & Druck",
                    "entities": [
                        {"entity": "sensor.wp1_sauggas_evi_temperatur", "name": "Sauggas EVI Temperatur"},
                        {"entity": "sensor.wp1_verdampfungstemperatur_evi", "name": "Verdampfungstemperatur EVI"},
                        {"entity": "sensor.wp1_verflussigungstemperatur_evi", "name": "Verflüssigungstemperatur EVI"},
                        {"entity": "sensor.wp1_uberhitzung_evi", "name": "Überhitzung EVI"},
                        {"entity": "sensor.wp1_verflussigungsdruck_evi", "name": "Verflüssigungsdruck EVI"},
                    ],
                }
            ],
        },
        {
            "title": "Weitere Sensoren",
            "type": "grid",
            "cards": [
                {
                    "type": "entities",
                    "title": "Leistung & Laufzeiten",
                    "entities": [
                        {"entity": "sensor.wp1_volumenstrom", "name": "WP1 Volumenstrom"},
                        {"entity": "sensor.wp1_letzte_laufzeit_pumpe", "name": "Letzte Laufzeit Pumpe"},
                        {"entity": "sensor.wp1_letzte_laufzeit_warmwasser", "name": "Letzte Laufzeit Warmwasser"},
                    ],
                },
                {
                    "type": "entities",
                    "title": "Sollwerte",
                    "entities": [
                        {"entity": "sensor.raum_soll_temperatur", "name": "Raum-Soll-Temperatur"},
                        {"entity": "sensor.warmwasser_soll_temperatur", "name": "Warmwasser-Soll-Temperatur"},
                        {"entity": "sensor.vorlauf_soll_temperatur", "name": "Vorlauf Soll-Temperatur"},
                    ],
                },
                {
                    "type": "entities",
                    "title": "Mischer & Steuerung",
                    "entities": [
                        {"entity": "sensor.mlt1_vorlauf_soll_temperatur", "name": "MLT1 Vorlauf Soll-Temperatur"},
                        {"entity": "sensor.mlt1_vorlauf_ist_temperatur", "name": "MLT1 Vorlauf Ist-Temperatur"},
                        {"entity": "sensor.mlt1_mischerposition", "name": "MLT1 Mischerposition"},
                        {"entity": "sensor.aktuelle_schritte_cl1", "name": "Aktuelle Schritte CL1"},
                        {"entity": "sensor.aktuelle_schritte_cl2", "name": "Aktuelle Schritte CL2"},
                    ],
                },
                {
                    "type": "entities",
                    "title": "Weitere Temperaturen",
                    "entities": [
                        {"entity": "sensor.mischer_ist_temperatur", "name": "Mischer Ist-Temperatur"},
                        {"entity": "sensor.abtaufuhler_ist_temperatur", "name": "Abtaufühler Ist-Temperatur"},
                        {"entity": "sensor.reservefuhler_1_temperatur", "name": "Reservefühler 1 Temperatur"},
                        {"entity": "sensor.reservefuhler_2_temperatur", "name": "Reservefühler 2 Temperatur"},
                        {"entity": "sensor.reservefuhler_3_temperatur", "name": "Reservefühler 3 Temperatur"},
                    ],
                },
            ],
        },
    ],
}

# Complete dashboard structure showing how to add the view
DASHBOARD_EXAMPLE = {"views": [{"title": "Home", "path": "default_view", "cards": []}, DASHBOARD_VIEW_CONFIG]}
