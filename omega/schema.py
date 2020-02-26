import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType

from omega.model import user, watch


class WatchObject(SQLAlchemyObjectType):
    class Meta:
        model = watch.Watch
        interfaces = (graphene.relay.Node,)


class UserObject(SQLAlchemyObjectType):
    class Meta:
        model = user.User
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_watches = SQLAlchemyConnectionField(WatchObject)
    all_users = SQLAlchemyConnectionField(UserObject)


# noinspection PyTypeChecker
query_schema = graphene.Schema(query=Query)
