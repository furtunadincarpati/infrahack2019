import json
import pickle
from lib.db import MongoClient
import requests
import time
import csv


def get_faults() -> []:
    return {x: 1 for x in pickle.load(open("data/faults.pkl", "rb"))}
    url = "https://europe-west1-infrahack.cloudfunctions.net/lifts-nr"

    re = requests.get(url, params={"timestamp": time.time(),
                                   "events_lookback_period_sec": 0}, timeout=5)
    ret_arr = dict()
    for lift in [x for x in re.json()['data'] if x['currently_operational'] is False]:

        if lift.get("events") != []:
            ret_arr[lift.get("lift_id")] = lift.get("events")[0].get("start")

        else:
            ret_arr[lift.get("lift_id")] = None

    return ret_arr


def load_cms_faults() -> []:
    out_data = dict()
    with open("data/Event Details.csv", newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        counter = 0
        for row in spamreader:
            counter += 1
            if counter == 1:
                continue

            if row:
                emu_id = row[0].split(" - ")[0]
                restored = row[4]
                if restored == "":  # -> lift is still broken
                    t = time.strptime("/".join(row[3].split("/")[:2] + [row[3].split("/")[-1][2:]]), '%d/%m/%y %H:%M')
                    out_data[emu_id] = time.mktime(t)

    return out_data


def prepare_faults(c: MongoClient, *, option="all") -> [dict]:
    """Prepares and cleans Fault data

    :return:
    """

    try:

        if option in ["all", "faults"]:
            stations = c.get_all()

        elif option == "incidents":
            stations = c.get_incidents()

        if option == "faults":
            faulty_stations = []

        faults = {}
        faults.update(get_faults())
        print(">>", faults)
        faults.update(load_cms_faults())
        print(">>", faults)
        for index, station in enumerate(stations.copy()):

            station["incidents"] = station.setdefault('incidents', [])
            station["_id"] = str(station["_id"])
            station['last_fault'] = []
            station["lift_status"] = []
            fault = 0
            working = 0

            for lift in station.get("lifts"):
                if lift in faults.keys():
                    station['lift_status'].append((lift, False))
                    fault += 1

                    station['last_fault'].append(faults[lift])

                else:
                    station['lift_status'].append((lift, True))
                    working += 1

            station["faulty_lifts"] = fault
            station["working_lifts"] = working
            station["total_lifts"] = working + fault

            if station['last_fault'] != [] and station['avg_repair'] != "no data":
                station['last_fault'] = max(station['last_fault'])
                station['time_passed'] = time.time() - int(station['last_fault'])
                station["fixed_aprox"] = round((int(station['avg_repair']) - int(station['time_passed'])) / 3600, 1)

            elif station['last_fault'] != [] and station['avg_repair'] == "no data":
                station["fixed_aprox"] = -1
                station["fixed_aprox"] = 3.2

            else:
                station['last_fault'] = None
                station['time_passed'] = None
                station["fixed_aprox"] = None

            if option == "faults":

                if station["faulty_lifts"] != 0:
                    faulty_stations.append(station)

        if option == "faults":
            stations = faulty_stations
        json.dump(stations, open("data/%s.json" % option, "w"))
        pickle.dump(stations, open("data/%s.pickle" % option, "wb"))

    except Exception as e:
        print(">> error:\n", e)
        stations = pickle.load(open("data/%s.pickle" % option, "rb"))

    return stations
