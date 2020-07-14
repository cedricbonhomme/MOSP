#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from flask_restx import Namespace, Resource, fields, reqparse, abort

from mosp.bootstrap import db
from mosp.models import JsonObject
from mosp.web.views.api.v2.common import auth_func


object_ns = Namespace(
    "object", description="object related operations"
)


# Argument Parsing
parser = reqparse.RequestParser()
parser.add_argument("uuid", type=str, help="The UUID of the object.")
parser.add_argument("name", type=str, help="The name of the object.")
parser.add_argument("page", type=int, required=False, default=1, help="Page number")
parser.add_argument("per_page", type=int, required=False, default=10, help="Page size")


# Response marshalling
object = object_ns.model(
    "Object",
    {
        "name": fields.String(description="The object name."),
        "description": fields.String(description="The object description."),
        "last_updated": fields.DateTime(description="Updated time of the object."),
        "json_object": fields.Raw(description="The object."),
    },
)

metadata = object_ns.model(
    "metadata",
    {
        "count": fields.String(
            readonly=True, description="Total number of the items of the data."
        ),
        "offset": fields.String(
            readonly=True,
            description="Position of the first element of the data from the total data amount.",
        ),
        "limit": fields.String(readonly=True, description="Requested limit data."),
    },
)

object_list_fields = object_ns.model(
    "ObjectsList",
    {
        "metadata": fields.Nested(
            metadata, description="Metada related to the result."
        ),
        "data": fields.List(fields.Nested(object), description="List of objects."),
    },
)


@object_ns.route("/")
class ObjectsList(Resource):
    """Create new objects."""

    @object_ns.doc("list_objects")
    @object_ns.expect(parser)
    @object_ns.marshal_list_with(object_list_fields)
    def get(self):
        """List all objects."""

        args = parser.parse_args()
        offset = args.pop("page", 1) - 1
        limit = args.pop("per_page", 10)
        object_uuid = args.pop("uuid", None)
        args = {k: v for k, v in args.items() if v is not None}

        result = {
            "data": [],
            "metadata": {"count": 0, "offset": offset, "limit": limit,},
        }

        try:
            query = JsonObject.query
            # Filter on attribute of the object
            for arg in args:
                if hasattr(JsonObject, arg):
                    query = query.filter(getattr(JsonObject, arg) == args[arg])

            # Filter on other attributes
            if object_uuid:
                query = query.filter(
                    JsonObject.json_object[("uuid")].astext == str(object_uuid)
                )

            total = query.count()
            query = query.limit(limit)
            results = query.offset(offset * limit)
            count = total
        except Exception as e:
            print(e)

        result["data"] = results
        result["metadata"]["count"] = count

        return result, 200

    # @object_ns.doc("create_object")
    # @object_ns.expect(object)
    # @object_ns.marshal_with(object, code=201)
    # @auth_func
    # def post(self):
    #     """Create a new object."""
    #     new_object = JsonObject(**object_ns.payload)
    #     db.session.add(new_object)
    #     db.session.commit()
    #     return new_object, 201
