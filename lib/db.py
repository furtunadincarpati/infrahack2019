import time
import pymongo
from typing import Union
from settings import mongo_settings
from bson.objectid import ObjectId


class MongoClient:

    def __init__(self, uri: str):

        self.client = self.get_conn(uri)

        self.db = self.client[mongo_settings.get("db")]
        self.stations = self.db[mongo_settings.get("stations_collection")]

    def get_conn(self, uri: str) -> pymongo.MongoClient:
        return pymongo.MongoClient(uri)

    def get_station(self, emu: Union[str, int]) -> dict:
        return self.stations.find_one({"lifts": emu})

    def get_all(self) -> [dict]:
        stations = [x for x in self.stations.find({"lat": {"$ne": None}, "lng": {"$ne": None}})]
        for station in stations:
            try:
                del station['repair_times']

            except:
                station["avg_repair"] = "no data"

        return stations

    def get_incidents(self) -> [dict]:
        stations = [x for x in self.stations.find({"lat": {"$ne": None},
                                                   "lng": {"$ne": None},
                                                   "incidents": {"$ne": None}})]
        for station in stations:
            try:
                del station['repair_times']

            except:
                station["avg_repair"] = "no data"

        return stations

    def insert_incident(self, incident_type: int, station_id: str):
        """Insert a new incident into the database

        """

        if self.stations.find_one({"_id": ObjectId(station_id)}):
            self.stations.update({"_id": ObjectId(station_id)}, {"$push": {"incidents": {"incident_type": incident_type,
                                                                                         "timestamp": time.time(),
                                                                                         "user": "test-user"}
                                                                           }})
            return 200

        else:
            print(">> station with _id: <{%s}> not found" % station_id)
            return 400