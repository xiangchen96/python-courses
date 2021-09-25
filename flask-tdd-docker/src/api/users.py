from http import HTTPStatus

from flask import Blueprint, request
from flask_restx import Api, Resource, fields

from src import db
from src.api.models import User

users_blueprint = Blueprint("users", __name__)
api = Api(users_blueprint)

user = api.model(
    "User",
    {
        "id": fields.Integer(readOnly=True),
        "username": fields.String(required=True),
        "email": fields.String(required=True),
        "created_date": fields.DateTime,
    },
)


class UsersList(Resource):
    @api.expect(user, validate=True)
    def post(self):
        post_data = request.get_json()
        username = post_data.get("username")
        email = post_data.get("email")
        response_object = {}

        user = User.query.filter_by(email=email).first()
        if user:
            response_object["message"] = "Sorry. That email already exists."
            return response_object, HTTPStatus.BAD_REQUEST

        db.session.add(User(username=username, email=email))
        db.session.commit()

        response_object["message"] = f"{email} was added!"
        return response_object, HTTPStatus.CREATED

    @api.marshal_with(user, as_list=True)
    def get(self):
        return User.query.all(), HTTPStatus.OK


class Users(Resource):
    @api.marshal_with(user)
    def get(self, user_id):
        u = User.query.filter_by(id=user_id).first()
        if not u:
            api.abort(HTTPStatus.NOT_FOUND, f"User {user_id} does not exist")
        return u, HTTPStatus.OK

    def delete(self, user_id):
        response_object = {}
        u = User.query.filter_by(id=user_id).first()

        if not u:
            api.abort(HTTPStatus.NOT_FOUND, f"User {user_id} does not exist")

        db.session.delete(u)
        db.session.commit()

        response_object["message"] = f"{u.email} was removed!"
        return response_object, HTTPStatus.OK

    @api.expect(user, validate=True)
    def put(self, user_id):
        post_data = request.get_json()
        username = post_data.get("username")
        email = post_data.get("email")
        response_object = {}

        u = User.query.filter_by(id=user_id).first()
        if not u:
            api.abort(404, f"User {user_id} does not exist")

        if User.query.filter_by(email=email).first():
            response_object["message"] = "Sorry. That email already exists."
            return response_object, 400

        u.username = username
        u.email = email
        db.session.commit()

        response_object["message"] = f"{u.id} was updated!"
        return response_object, 200


api.add_resource(UsersList, "/users")
api.add_resource(Users, "/users/<int:user_id>")