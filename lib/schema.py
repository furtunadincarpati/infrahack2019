import time

from graphql import GraphQLError
import graphene
from lib.models import Station as StationModel
from lib.models import Incident as IncidentModel
from lib.models import StationFault as StationFaultModel
from lib.models import Fault as FaultModel
from graphene_mongo import MongoengineObjectType, MongoengineConnectionField
from graphene_mongo_extras.filtering.fields import FilteringConnectionField


class CustomNode(graphene.Node):
    class Meta:
        name = 'Node'
        description = "Custom node for correct mongo id resolution"

    @staticmethod
    def to_global_id(type, id):
        return id


class Station(MongoengineObjectType):
    class Meta:
        description = "Query a single a station"
        model = StationModel
        interfaces = (CustomNode, )


class InsertIncident(graphene.Mutation):
    class Meta:
        description = "This mutation is used to insert new incidents into mongo"

    class Arguments:
        user = graphene.String()
        incident_type = graphene.String()
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    station = graphene.Field(Station)

    def mutate(self, info, user, incident_type, id):

        station = StationModel.objects.get(id=id)

        station.update(push__incidents={"incident_type": incident_type,
                                        "timestamp": time.time(),
                                        "user": user})
        ok = True

        return InsertIncident(station=station, ok=ok)


class Incident(MongoengineObjectType):
    class Meta:
        model = IncidentModel
        interfaces = (CustomNode, )


class Fault(MongoengineObjectType):
    class Meta:
        description = "Query a single a fault"
        model = FaultModel
        interfaces = (CustomNode, )


class StationsWithFaults(MongoengineObjectType):
    class Meta:
        description = "Query all stations joined with faults"
        model = StationFaultModel

        interfaces = (CustomNode, )


class Query(graphene.ObjectType):
    class Meta:
        description = "Available queries for Uplift Project"

    # custom node for resolving the mongo object id correctly
    node = CustomNode.Field()

    stations = MongoengineConnectionField(StationsWithFaults,
                                          aggregation=graphene.types.json.JSONString(),
                                          description="Returns all stations joined with faults, "
                                                      "the aggregation attribute takes a Json string containing a mongo"
                                                      "$match aggregation for filtering")

    def resolve_stations(self, info, **kwargs):

        pipeline = [
            {"$lookup": {
                'from': FaultModel._get_collection_name(),
                'localField': '_id',
                'foreignField': 'station_id',
                'as': 'faults'
            }},
            {"$addFields": {
                "faults": "$faults.faulty_lifts"
            }}
        ]

        aggregation = kwargs.get("aggregation")
        if aggregation:

            if list(aggregation.keys())[0] == "$match":
                pipeline.append(aggregation)

            else:
                raise GraphQLError("Invalid aggregation stage, only $match is allowed")

        out = []
        for x in StationModel.objects.aggregate(*pipeline):
            if x.get("faults") != []:
                x["faults"] = [item for sublist in x.get("faults") for item in sublist]
            x.update({"id": x.get("_id")})
            x.pop("_id")
            out.append(StationFaultModel(**x))

        return out

    faults = FilteringConnectionField(Fault,
                                      description="Returns all faults from the database")

    station = CustomNode.Field(Station,
                               description="Queries one stations")

    fault = CustomNode.Field(Fault,
                             description="Queries one fault")


class Mutation(graphene.ObjectType):
    class Meta:
        description = "Available mutations for Uplift Project"

    insert_incident = InsertIncident.Field(
        description="Inserts new incident into mongoDB"
    )


schema = graphene.Schema(query=Query,
                         mutation=Mutation,
                         types=[Station, Fault, StationsWithFaults, Incident, InsertIncident])