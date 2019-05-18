import pickle
from lib.db import MongoClient
import requests
import time
import csv


def get_faults() -> []:

    url = "https://europe-west1-infrahack.cloudfunctions.net/lifts-nr"
    print(">> getting faults")

    try:
        re = requests.get(url, params={"timestamp": time.time(),
                                       "events_lookback_period_sec": 0}, timeout=5)
        return [x['lift_id'] for x in re.json()['data'] if x['currently_operational'] is False]

    except Exception as e:
        print(f">>api-call failed, using local data:\n{e}")
        return pickle.load(open("data/faults.pkl", "rb"))


def load_cms_faults() -> []:

    out_data = []
    with open("Event Details.csv", newline='') as csvfile:
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
                    out_data.append(emu_id)

    return out_data


def prepare_faults(c: MongoClient) -> [dict]:
    """Prepares and cleans Fault data

    :return:
    """

    try:
        stations = c.get_all()

        faults = get_faults()
        print(">>", faults)
        faults += load_cms_faults()
        print(">>", faults)
        for station in stations:

            del station["_id"]
            station["lift_status"] = []
            fault = 0
            working = 0
            for lift in station.get("lifts"):
                if lift in faults:
                    station['lift_status'].append((lift, False))
                    fault += 1

                else:
                    station['lift_status'].append((lift, True))
                    working += 1

            station["faulty_lifts"] = fault
            station["working_lifts"] = working
            station["total_lifts"] = working + fault

        pickle.dump(stations, open("data.pickle", "wb"))

    except Exception as e:
        print(">> error:\n", e)
        stations = pickle.load(open("data.pickle", "rb"))

    return stations
