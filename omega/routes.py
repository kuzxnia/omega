import logging

from flask_graphql import GraphQLView

log = logging.getLogger(__name__)


def register_endpoints(app):
    from omega.mutation import mutation_schema
    from omega.schema import query_schema

    app.add_url_rule(
        "/graphql-query",
        view_func=GraphQLView.as_view(
            "graphql-query", schema=query_schema, graphiql=True
        ),
    )
    app.add_url_rule(
        "/graphql-mutation",
        view_func=GraphQLView.as_view(
            "graphql-mutation", schema=mutation_schema, graphiql=True
        ),
    )
