import pickle
from lib.db import MongoClient
import requests
import time


def get_faults() -> []:

    url = "https://europe-west1-infrahack.cloudfunctions.net/lifts-nr"
    print(">> getting faults")

    try:
        re = requests.get(url, params={"timestamp": time.time(),
                                       "events_lookback_period_sec": 0})
        return [x['lift_id'] for x in re.json()['data'] if x['currently_operational'] is False]

    except Exception as e:
        print(f">>api-call failed, using local data:\n{e}")
        return pickle.load(open("faults.pkl", "rb"))


def prepare_faults(c: MongoClient) -> [dict]:
    """Prepares and cleans Fault data

    :return:
    """

    stations = c.get_all()
    faults = get_faults()

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

    return stations
