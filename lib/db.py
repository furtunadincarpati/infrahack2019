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