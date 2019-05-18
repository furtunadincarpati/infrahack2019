import time

import pymongo
from typing import Union


class MongoClient:

    def __init__(self, uri: str,
                 db_name: str = "infrahack",
                 station_col: str = "stations"):

        self.client = self.get_conn(uri)

        self.db = self.client[db_name]
        self.stations = self.db[station_col]

    def get_conn(self, uri: str) -> pymongo.MongoClient:
        return pymongo.MongoClient(uri)

    def get_station(self, emu: Union[str, int]) -> dict:
        return self.stations.find_one({"lifts": emu})

    def get_all(self) -> [dict]:
        return [x for x in self.stations.find({"lat": {"$ne": None}, "lng": {"$ne": None}})]

    def insert_incident(self, incident_type: str, station_name: str):
        """Insert a new incident into the database

        """

        if self.stations.find_one({"name" : station_name}):
            self.stations.update({"name": station_name}, {"$push": {"incidents": {"incident_type": incident_type,
                                                                                  "timestamp": time.time()}}})
        else:
            print(f">> station {station_name} not found")
