#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from flask_restx import Namespace, Resource, fields, reqparse, abort

from mosp.bootstrap import db
from mosp.models import Organization


organization_ns = Namespace(
    "organization", description="organization related operations"
)


# Argument Parsing
parser = reqparse.RequestParser()
parser.add_argument("name", type=str, help="The name of the organization.")
parser.add_argument("organization_type", type=str, help="The type of the organization.")
parser.add_argument("page", type=int, required=False, default=1, help="Page number")
parser.add_argument("per_page", type=int, required=False, default=10, help="Page size")


# Response marshalling
organization = organization_ns.model(
    "Organization",
    {
        "name": fields.String(description="The organization name."),
        "description": fields.String(description="The organization description."),
        "organization_type": fields.String(description="The type of the organization."),
        "last_updated": fields.DateTime(description="Updated time of the schema."),
    },
)

metadata = organization_ns.model(
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

organization_list_fields = organization_ns.model(
    "OrganizationsList",
    {
        "metadata": fields.Nested(
            metadata, description="Metada related to the result."
        ),
        "data": fields.List(
            fields.Nested(organization), description="List of organizations."
        ),
    },
)


@organization_ns.route("/")
class OrganizationsList(Resource):
    """Create new organization."""

    @organization_ns.doc("list_organizations")
    @organization_ns.expect(parser)
    @organization_ns.marshal_list_with(organization_list_fields)
    def get(self):
        """List all organizations."""

        args = parser.parse_args()
        offset = args.pop("page", 1) - 1
        limit = args.pop("per_page", 10)
        args = {k: v for k, v in args.items() if v is not None}

        result = {
            "data": [],
            "metadata": {
                "count": 0,
                "offset": offset,
                "limit": limit,
            },
        }

        try:
            query = Organization.query
            for arg in args:
                if hasattr(Organization, arg):
                    query = query.filter(getattr(Organization, arg) == args[arg])
            total = query.count()
            query = query.limit(limit)
            results = query.offset(offset * limit)
            count = total
        except Exception as e:
            print(e)

        result["data"] = results
        result["metadata"]["count"] = count

        return result, 200

    # @organization_ns.doc("create_organization")
    # @organization_ns.expect(organization)
    # @organization_ns.marshal_with(organization, code=201)
    # @auth_func
    # def post(self):
    #     """Create a new organization."""
    #     new_organization = Organization(**organization_ns.payload)
    #     db.session.add(new_organization)
    #     db.session.commit()
    #     return new_organization, 201
