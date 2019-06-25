from mongoengine import Document
from mongoengine.fields import StringField, ListField, IntField, FloatField, \
    EmbeddedDocument, EmbeddedDocumentField, ObjectIdField


class Incident(EmbeddedDocument):
    incident_type = StringField()
    user = StringField()
    timestamp = FloatField()


class Station(Document):
    meta = {'collection': 'stations'}
    name = StringField()
    lng = StringField()
    lat = StringField()
    lifts = ListField(StringField())
    repair_times = ListField(IntField())
    avg_repair = FloatField()
    incidents = ListField(EmbeddedDocumentField(Incident))


class Fault(Document):
    meta = {'collection': 'faults'}
    station_id = ObjectIdField(required=True, unique=True)
    faulty_lifts = ListField(StringField())


class StationFault(Document):
    name = StringField()
    lng = StringField()
    lat = StringField()
    lifts = ListField(StringField())
    repair_times = ListField(IntField())
    avg_repair = FloatField()
    incidents = ListField(EmbeddedDocumentField(Incident))
    faults = ListField(StringField())

