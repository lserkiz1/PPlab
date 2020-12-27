from flask import Blueprint, jsonify, request
import db_utils
from middlewares import db_lifecycle
from models import Users, calendar, events
from schemas import (
    Credentials,
    AccessToken,
    UserData,
    ListUsersRequest,
    UserToCreate,
    UserToUpdate,
    StatusResponse,
    calendarData,
    EventToCreate,
    EventToUpdate,  CaseToSend,
)

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route("/auth", methods=["POST"])
def auth():
    Credentials().load(request.json)
    return jsonify(AccessToken().dump({"access_token": ""}))


@api_blueprint.route("/user", methods=["GET"])
@db_lifecycle
def list_users():
    args = ListUsersRequest().load(request.args)
    users = db_utils.list_users(
        args.get("email"), args.get("first_name"), args.get("last_name")
    )
    return jsonify(UserData(many=True).dump(users))


@api_blueprint.route("/user", methods=["POST"])
@db_lifecycle
def create_user():
    user_data = UserToCreate().load(request.json)
    user = db_utils.create_entry(Users, **user_data)
    return jsonify(UserData().dump(user))


@api_blueprint.route("/user/<int:user_id>", methods=["GET"])
@db_lifecycle
def get_user_by_id(user_id):
    user = db_utils.get_entry_by_uid(Users, user_id)
    return jsonify(UserData().dump(user))


@api_blueprint.route("/user/<int:user_id>", methods=["PUT"])
@db_lifecycle
def update_user(user_id):
    user_data = UserToUpdate().load(request.json)
    user = db_utils.get_entry_by_uid(Users, user_id)
    db_utils.update_entry(user, **user_data)
    return jsonify(StatusResponse().dump({"code": 200}))


@api_blueprint.route("/user/<int:user_id>", methods=["DELETE"])
@db_lifecycle
def delete_user(user_id):
    db_utils.delete_entry(Users, user_id)
    return jsonify(StatusResponse().dump({"code": 200}))


@api_blueprint.route("/calendar", methods=["GET"])
@db_lifecycle
def list_calendar():
    events = db_utils.list_events()
    return jsonify(calendarData(many=True).dump(calendar))


@api_blueprint.route("/calendar", methods=["POST"])
@db_lifecycle
def create_calendar():
    calendar_data = EventToCreate().load(request.json)
    event = db_utils.create_entry(events, **calendar_data, case=0)
    return jsonify(calendarData().dump(event))


@api_blueprint.route("/calendar/<int:calendar_id>", methods=["GET"])
@db_lifecycle
def get_calendar_by_id(calendar_id):
    event = db_utils.get_entry_by_uid(events, calendar_id)
    return jsonify(calendarData().dump(event))


@api_blueprint.route("/calendar/<int:calendar_id>", methods=["PUT"])
@db_lifecycle
def update_event(calendar_id):
    calendar_data = EventToUpdate().load(request.json)
    event = db_utils.get_entry_by_uid(events, calendar_id)
    db_utils.update_entry(event, **calendar_data)
    return jsonify(StatusResponse().dump({"code": 200}))


@api_blueprint.route("/calendar/<int:calendar_id>", methods=["DELETE"])
@db_lifecycle
def delete_event(calendar_id):
    db_utils.delete_entry(events, calendar_id)
    return jsonify(StatusResponse().dump({"code": 200}))


@api_blueprint.route("/calendar/<int:calendar_id>/send-case", methods=["POST"])
@db_lifecycle
def send_case(calendar_id):
    events_data = CaseToSend().load(request.json)
    events = db_utils.create_entry(
        calendar,
        from_calendar_uid=calendar_id or None,
        to_calendar_uid=events_data["to_calendar"],
        tekst=events_data["text"],
    )
    return jsonify(calendarData().dump(calendar))


@api_blueprint.route("/calendar/<int:calendar_id>/events", methods=["GET"])
@db_lifecycle
def list_calendar_events(calendar_id):
    events = db_utils.list_events_for_calendar(calendar_id)
    return jsonify(calendarData(many=True).dump(events))