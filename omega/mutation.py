import graphene

from omega.extensions import db
from omega.model.user import User
from omega.schema import Query, UserObject


class CreateUser(graphene.Mutation):
    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        login = graphene.String(required=True)
        email_address = graphene.String(required=True)
        password = graphene.String(required=True)

    User = graphene.Field(lambda: UserObject)

    def mutate(self, info, first_name, last_name, login, email_address, password):
        user = User(
            first_name=first_name,
            last_name=last_name,
            login=login,
            email_address=email_address,
            password=password,
        )
        db.session.add(user)
        db.session.commit()
        return user


class Mutation(graphene.ObjectType):
    save_user = CreateUser.Field()


mutation_schema = graphene.Schema(query=Query, mutation=Mutation)
