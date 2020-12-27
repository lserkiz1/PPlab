from flask_bcrypt import generate_password_hash
from marshmallow import validate, Schema, fields


class Credentials(Schema):
    email = fields.String(validate=validate.Email())
    password = fields.String()


class AccessToken(Schema):
    access_token = fields.String()


class ListUsersRequest(Schema):
    email = fields.String(validate=validate.Email())
    first_name = fields.String()
    last_name = fields.String()


class UserData(Schema):
    uid = fields.Integer()
    email = fields.String(validate=validate.Email())
    first_name = fields.String()
    last_name = fields.String()


class UserToCreate(Schema):
    email = fields.String(validate=validate.Email())
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )
    first_name = fields.String()
    last_name = fields.String()


class UserToUpdate(Schema):
    email = fields.String(validate=validate.Email())
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )
    first_name = fields.String()
    last_name = fields.String()


class calendarData(Schema):
    uid = fields.Integer()
    name = fields.String()
    owner_uid = fields.Integer()
    case = fields.Integer()


class EventToCreate(Schema):
    name = fields.String()


class EventToUpdate(Schema):
    name = fields.String()


class CaseToSend(Schema):
    to_wallet = fields.Integer()
    tekst = fields.String()


class EventsData(Schema):
    uid = fields.Integer()
    from_calendar = fields.Integer(attribute="from_calendar_uid")
    to_calendar= fields.Integer(attribute="to_calendar_uid")
    tekst = fields.String()
    datetime = fields.DateTime()


class StatusResponse(Schema):
    code = fields.Integer()
    type = fields.String(default="OK")
    message = fields.String(default="OK")