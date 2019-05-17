import requests
import time


def get_faults() -> []:

    url = "https://europe-west1-infrahack.cloudfunctions.net/lifts-nr"

    re = requests.get(url, params={"timestamp": time.time(),
                                   "events_lookback_period_sec": 0})

    return [x for x in re.json()['data'] if x['currently_operational'] is False]