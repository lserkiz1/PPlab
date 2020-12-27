from datetime import datetime
from unittest.mock import ANY

from flask import url_for
from flask_bcrypt import generate_password_hash
from flask_testing import TestCase

from prukladne7 import db_utils
from prukladne7.main import app
from prukladne7.models import Users, Session, Calendar, Events, BaseModel, engine


class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.create_tables()

        self.admin_credentials = {
            "username": "admin-aec8084845b41a6952d46cbaa1c9b798659487ffd133796d95d05ba45d9096c2",
            "password": "super-secret",
        }

        self.user_1_data = {
            "email": "test_1@example.com",
            "password": "123",
            "first_name": "First1",
            "last_name": "Last1",
        }
        self.user_1_data_hashed = {
            **self.user_1_data,
            "password": generate_password_hash(self.user_1_data["password"]),
        }
        self.user_1_credentials = {
            "username": self.user_1_data["email"],
            "password": self.user_1_data["password"],
        }

        self.user_2_data = {
            "email": "test_2@example.com",
            "password": "123",
            "first_name": "First2",
            "last_name": "Last2",
        }
        self.user_2_data_hashed = {
            **self.user_2_data,
            "password": generate_password_hash(self.user_2_data["password"]),
        }
        self.user_2_credentials = {
            "username": self.user_2_data["email"],
            "password": self.user_2_data["password"],
        }

        self.calendar_1_data = {"name": "Calendar A", "owner_uid": None, "text": 0}
        self.calendar_2_data = {"name": "Calendar B", "owner_uid": None, "text": 0}
        self.calendar_3_data = {"name": "Calendar B", "owner_uid": None, "text": 0}

    def tearDown(self):
        self.close_session()

    def create_tables(self):
        BaseModel.metadata.drop_all(engine)
        BaseModel.metadata.create_all(engine)

    def close_session(self):
        Session().close()

    def create_app(self):
        return app

    def get_auth_headers(self, credentials):
        resp = self.client.post(url_for("auth"), json=credentials)
        access_token = resp.json["access_token"]
        return {'AUthorization': f'JWT {access_token}'}


class TestAuthentication(BaseTestCase):
    def test_admin_auth(self):
        resp = self.client.post(url_for("auth"), json=self.admin_credentials)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {"access_token": ANY})

    def test_user_auth(self):
        db_utils.create_entry(Users, **self.user_1_data_hashed)

        resp = self.client.post(url_for("auth"), json=self.user_1_credentials)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {"access_token": ANY})


class TestListUsers(BaseTestCase):
    def test_list_users(self):
        db_utils.create_entry(Users, **self.user_1_data_hashed)
        db_utils.create_entry(Users, **self.user_2_data_hashed)

        resp = self.client.get(
            url_for("api.list_users"),
            headers=self.get_auth_headers(self.admin_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, [
            {
                'uid': ANY,
                'email': self.user_1_data['email'],
                'first_name': self.user_1_data['first_name'],
                'last_name': self.user_1_data['last_name'],
            },
            {
                'uid': ANY,
                'email': self.user_2_data['email'],
                'first_name': self.user_2_data['first_name'],
                'last_name': self.user_2_data['last_name'],
            },
        ])

    def test_unauthorized(self):
        resp = self.client.get(url_for("api.list_users"))
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })

    def test_not_admin(self):
        db_utils.create_entry(Users, **self.user_1_data_hashed)

        resp = self.client.get(
            url_for("api.list_users"),
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })


class TestCreateUser(BaseTestCase):
    def test_create_user(self):
        resp = self.client.post(
            url_for("api.create_user"),
            json=self.user_1_data,
            headers=self.get_auth_headers(self.admin_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'uid': ANY,
            'email': self.user_1_data['email'],
            'first_name': self.user_1_data['first_name'],
            'last_name': self.user_1_data['last_name'],
        })
        self.assertTrue(
            Session().query(Users).filter_by(email=self.user_1_data['email']).one()
        )

    def test_unauthorized(self):
        resp = self.client.post(url_for("api.create_user"), json=self.user_1_data)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })
        self.assertFalse(
            Session().query(Users).filter_by(email=self.user_1_data['email']).one_or_none()
        )

    def test_not_admin(self):
        db_utils.create_entry(Users, **self.user_1_data_hashed)

        resp = self.client.post(
            url_for("api.create_user"),
            json=self.user_2_data,
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })
        self.assertFalse(
            Session().query(Users).filter_by(email=self.user_2_data['email']).one_or_none()
        )


class TestGetUser(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = db_utils.create_entry(Users, **self.user_1_data_hashed)

    def test_get_user_by_id(self):
        resp = self.client.get(
            url_for("api.get_user_by_id", user_id=self.user.uid),
            headers=self.get_auth_headers(self.admin_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'uid': self.user.uid,
            'email': self.user_1_data['email'],
            'first_name': self.user_1_data['first_name'],
            'last_name': self.user_1_data['last_name'],
        })

    def test_unauthorized(self):
        resp = self.client.get(url_for("api.get_user_by_id", user_id=self.user.uid))

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })

    def test_not_admin(self):
        resp = self.client.get(
            url_for("api.get_user_by_id", user_id=self.user.uid),
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'uid': self.user.uid,
            'email': self.user_1_data['email'],
            'first_name': self.user_1_data['first_name'],
            'last_name': self.user_1_data['last_name'],
        })


class TestUpdateUser(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = db_utils.create_entry(Users, **self.user_1_data_hashed)
        self.user_2 = db_utils.create_entry(Users, **self.user_2_data_hashed)

    def test_update_user(self):
        resp = self.client.put(
            url_for("api.update_user", user_id=self.user_1.uid),
            json={
                **self.user_1_data,
                "first_name": "UpdatedFirst"
            },
            headers=self.get_auth_headers(self.admin_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'code': 200,
            'type': 'OK',
            'message': ANY
        })
        self.assertTrue(
            Session().query(Users).filter_by(first_name='UpdatedFirst').one()
        )

    def test_unauthorized(self):
        resp = self.client.put(
            url_for("api.update_user", user_id=self.user_1.uid),
            json={
                **self.user_1_data,
                "first_name": "UpdatedFirst"
            },
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })
        self.assertFalse(
            Session().query(Users).filter_by(first_name='UpdatedFirst').one_or_none()
        )

    def test_self_update(self):
        resp = self.client.put(
            url_for("api.update_user", user_id=self.user_1.uid),
            json={
                **self.user_1_data,
                "first_name": "UpdatedFirst"
            },
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'code': 200,
            'type': 'OK',
            'message': ANY
        })
        self.assertTrue(
            Session().query(Users).filter_by(first_name='UpdatedFirst').one()
        )

    def test_update_another_user(self):
        resp = self.client.put(
            url_for("api.update_user", user_id=self.user_2.uid),
            json={
                **self.user_2_data,
                "first_name": "UpdatedFirst"
            },
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })
        self.assertFalse(
            Session().query(Users).filter_by(first_name='UpdatedFirst').one_or_none()
        )


class TestDeleteUser(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = db_utils.create_entry(Users, **self.user_1_data_hashed)
        self.user_2 = db_utils.create_entry(Users, **self.user_2_data_hashed)

    def test_delete_user(self):
        resp = self.client.delete(
            url_for("api.delete_user", user_id=self.user_1.uid),
            headers=self.get_auth_headers(self.admin_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'code': 200,
            'type': 'OK',
            'message': ANY
        })
        self.assertFalse(
            Session().query(Users).filter_by(uid=self.user_1.uid).one_or_none()
        )

    def test_unauthorized(self):
        resp = self.client.delete(url_for("api.delete_user", user_id=self.user_1.uid))

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })
        self.assertTrue(
            Session().query(Users).filter_by(uid=self.user_1.uid).one_or_none()
        )

    def test_self_delete(self):
        resp = self.client.delete(
            url_for("api.delete_user", user_id=self.user_1.uid),
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'code': 200,
            'type': 'OK',
            'message': ANY
        })
        self.assertFalse(
            Session().query(Users).filter_by(uid=self.user_1.uid).one_or_none()
        )

    def test_update_another_user(self):
        resp = self.client.delete(
            url_for("api.delete_user", user_id=self.user_2.uid),
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })
        self.assertTrue(
            Session().query(Users).filter_by(uid=self.user_2.uid).one_or_none()
        )


class TestListEvents(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = db_utils.create_entry(Users, **self.user_1_data_hashed)
        self.user_2 = db_utils.create_entry(Users, **self.user_2_data_hashed)
        db_utils.create_entry(events, **{
            **self.calendar_1_data, 'owner_uid': self.user_1.uid
        })
        db_utils.create_entry(Wallets, **{
            **self.calendar_2_data, 'owner_uid': self.user_2.uid
        })

    def test_list_events(self):
        resp = self.client.get(
            url_for("api.list_events"),
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, [
            {
                'uid': ANY,
                'name': self.calendar_1_data['name'],
                'funds': self.calendar_1_data['text'],
                'owner_uid': self.user_1.uid
            },
        ])

    def test_list_events_by_admin(self):
        resp = self.client.get(
            url_for("api.list_events"),
            headers=self.get_auth_headers(self.admin_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, [
            {
                'uid': ANY,
                'name': self.calendar_1_data['name'],
                'text': self.calendar_1_data['text'],
                'owner_uid': self.user_1.uid
            },
            {
                'uid': ANY,
                'name': self.calendar_1_data['name'],
                'text': self.calendar_1_data['text'],
                'owner_uid': self.user_2.uid
            },
        ])

    def test_unauthorized(self):
        resp = self.client.get(url_for("api.list_events"))

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })


class TestCreateEvent(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = db_utils.create_entry(Users, **self.user_1_data_hashed)

    def test_create_event(self):
        resp = self.client.post(
            url_for("api.create_event"),
            json={"name": self.calendar_1_data["name"]},
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'uid': ANY,
            'name': self.calendar_1_data['name'],
            'text': 0,
            'owner_uid': self.user_1.uid
        })

    def test_unauthorized(self):
        resp = self.client.post(
            url_for("api.create_event"),
            json={"name": self.calendar_1_data["name"]},
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })


class TestGetEvent(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = db_utils.create_entry(Users, **self.user_1_data_hashed)
        self.user_2 = db_utils.create_entry(Users, **self.user_2_data_hashed)
        self.calendar = db_utils.create_entry(events, **{
            **self.calendar_1_data, 'owner_uid': self.user_1.uid
        })

    def test_get_event(self):
        resp = self.client.get(
            url_for("api.get_event_by_id", event_id=self.event.uid),
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'uid': ANY,
            'name': self.calendar_1_data['name'],
            'funds': 0,
            'owner_uid': self.user_1.uid
        })

    def test_get_event_by_wrong_user(self):
        resp = self.client.get(
            url_for("api.get_event_by_id", event_id=self.event.uid),
            headers=self.get_auth_headers(self.user_2_credentials),
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {
            'code': 404,
            'type': 'NOT_FOUND',
            'message': ANY
        })

    def test_unauthorized(self):
        resp = self.client.get(
            url_for("api.get_event_by_id", event_id=self.event.uid)
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })


class TestUpdateEvent(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = db_utils.create_entry(Users, **self.user_1_data_hashed)
        self.user_2 = db_utils.create_entry(Users, **self.user_2_data_hashed)
        self.calendar = db_utils.create_entry(Wallets, **{
            **self.wcalendar_1_data, 'owner_uid': self.user_1.uid
        })

    def test_update_event(self):
        resp = self.client.put(
            url_for("api.update_event", event_id=self.event.uid),
            json={"name": "Updated event A"},
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'code': 200,
            'type': 'OK',
            'message': ANY
        })
        self.assertTrue(
            Session().query(events).filter_by(name="Updated event A").one()
        )

    def test_update_eventt_by_wrong_user(self):
        resp = self.client.put(
            url_for("api.update_event", event_id=self.event.uid),
            json={"name": "Updated Event A"},
            headers=self.get_auth_headers(self.user_2_credentials),
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {
            'code': 404,
            'type': 'NOT_FOUND',
            'message': ANY
        })
        self.assertFalse(
            Session().query(events).filter_by(name="Updated event A").one_or_none()
        )

    def test_unauthorized(self):
        resp = self.client.put(
            url_for("api.update_event", event_id=self.event.uid),
            json={"name": "Updated event A"},
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })
        self.assertFalse(
            Session().query(events).filter_by(name="Updated event A").one_or_none()
        )


class TestDeleteEvent(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = db_utils.create_entry(Users, **self.user_1_data_hashed)
        self.user_2 = db_utils.create_entry(Users, **self.user_2_data_hashed)
        self.calendar = db_utils.create_entry(events, **{
            **self.calendar_1_data, 'owner_uid': self.user_1.uid
        })

    def test_delete_event(self):
        resp = self.client.delete(
            url_for("api.delete_event", event_id=self.event.uid),
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'code': 200,
            'type': 'OK',
            'message': ANY
        })
        self.assertFalse(
            Session().query(events).filter_by(uid=self.event.uid).one_or_none()
        )

    def test_delete_event_by_wrong_user(self):
        resp = self.client.delete(
            url_for("api.delete_event", event_id=self.event.uid),
            headers=self.get_auth_headers(self.user_2_credentials),
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {
            'code': 404,
            'type': 'NOT_FOUND',
            'message': ANY
        })
        self.assertTrue(
            Session().query(events).filter_by(uid=self.event.uid).one_or_none()
        )

    def test_unauthorized(self):
        resp = self.client.delete(
            url_for("api.delete_event", event_id=self.event.uid),
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })
        self.assertTrue(
            Session().query(events).filter_by(uid=self.event.uid).one_or_none()
        )


class TestSendCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = db_utils.create_entry(Users, **self.user_1_data_hashed)
        self.user_2 = db_utils.create_entry(Users, **self.user_2_data_hashed)
        self.calendar_1 = db_utils.create_entry(events, **{
            **self.calendar_1_data, 'owner_uid': self.user_1.uid, "text": 100
        })
        self.calendar_2 = db_utils.create_entry(events, **{
            **self.calendar_2_data, 'owner_uid': self.user_2.uid
        })

    def test_send_case(self):
        resp = self.client.post(
            url_for("api.send_case", event_id=self.calendar_1.uid),
            json={"to_calendar": self.calendar_2.uid, "text": 25},
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'uid': ANY,
            'from_calendar': self.calendar_1.uid,
            'to_calendar': self.calendar_2.uid,
            'text': 25,
            'datetime': ANY
        })
        self.assertTrue(
            Session().query(Events).filter_by(uid=resp.json['uid']).one()
        )
        self.assertEqual(
            Session().query(events.case).filter_by(uid=self.calendar_1.uid).one().case,
            75,
        )
        self.assertEqual(
            Session().query(events.case).filter_by(uid=self.calendar_2.uid).one().case,
            25,
        )

    def test_send_case_with_wrong_user(self):
        resp = self.client.post(
            url_for("api.send_case", event_id=self.calendar_1.uid),
            json={"to_calendar": self.calendar_2.uid, "text": 25},
            headers=self.get_auth_headers(self.user_2_credentials),
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {
            'code': 404,
            'type': 'NOT_FOUND',
            'message': ANY
        })
        self.assertEqual(
            Session().query(events.case).filter_by(uid=self.calendar_1.uid).one().case,
            100,
        )
        self.assertEqual(
            Session().query(events.case).filter_by(uid=self.calendar_2.uid).one().case,
            0,
        )

    def test_unauthorized(self):
        resp = self.client.post(
            url_for("api.send_case", calendar_id=self.calendar_1.uid),
            json={"to_calendar": self.calendar_2.uid, "text": 25},
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })
        self.assertEqual(
            Session().query(events.case).filter_by(uid=self.calendar_1.uid).one().case,
            100,
        )
        self.assertEqual(
            Session().query(events.case).filter_by(uid=self.calendar_2.uid).one().case,
            0,
        )


class TestListCalendarEvents(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user_1 = db_utils.create_entry(Users, **self.user_1_data_hashed)
        self.user_2 = db_utils.create_entry(Users, **self.user_2_data_hashed)

        self.calendar_1 = db_utils.create_entry(events, **{
            **self.calendar_1_data, 'owner_uid': self.user_1.uid, "text": 100
        })
        self.calendar_2 = db_utils.create_entry(events, **{
            **self.calendar_2_data, 'owner_uid': self.user_2.uid
        })
        self.calendar_3 = db_utils.create_entry(events, **{
            **self.calendar_3_data, 'owner_uid': self.user_1.uid
        })

        self.calendar_1_events_1_data = {
            "from_calendar_uid": self.calendar_1.uid,
            "to_calendar_uid": self.calendar_2.uid,
            "text": 10,
            "datetime": datetime.now(),
        }
        self.calendar_1_events_1 = db_utils.create_entry(
            Events, **self.calendar_1_events_1_data
        )

        self.calendar_1_events_2_data = {
            "from_calendar_uid": self.calendar_1.uid,
            "to_calendar_uid": self.calendar_2.uid,
            "text": 10,
            "datetime": datetime.now(),
        }
        self.calendar_1_events_2 = db_utils.create_entry(
            Events, **self.calendar_1_events_2_data
        )

        self.calendar_2_events_1_data = {
            "from_calendar_uid": self.calendar_2.uid,
            "to_calendar_uid": self.calendar_1.uid,
            "text": 5,
            "datetime": datetime.now(),
        }
        self.calendar_2_events_1 = db_utils.create_entry(
            Events, **self.calendar_2_events_1_data
        )

        self.calendar_2_events_2_data = {
            "from_calendar_uid": self.calendar_2.uid,
            "to_calendar_uid": self.calendar_3.uid,
            "text": 5,
            "datetime": datetime.now(),
        }
        self.calendar_2_events_2 = db_utils.create_entry(
            Events, **self.calendar_2_events_2_data
        )

    def test_list_calendar_events(self):
        resp = self.client.get(
            url_for("api.list_calendar_events", event_id=self.calendar_1.uid),
            headers=self.get_auth_headers(self.user_1_credentials),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, [
            {
                'uid': ANY,
                "from_calendar": self.calendar_1_events_1_data["from_calendar_uid"],
                "to_calendar": self.calendar_1_events_1_data["to_calendar_uid"],
                "text": self.calendar_1_events_1_data["text"],
                "datetime": self.calendar_1_events_1_data["datetime"].isoformat(),
            },
            {
                'uid': ANY,
                "from_calendar": self.calendar_1_events_2_data["from_calendar_uid"],
                "to_calendar": self.calendar_1_events_2_data["to_calendar_uid"],
                "text": self.calendar_1_events_2_data["text"],
                "datetime": self.calendar_1_events_2_data["datetime"].isoformat(),
            },
            {
                'uid': ANY,
                "from_calendar": self.calendar_2_events_1_data["from_calendar_uid"],
                "to_calendar": self.calendar_2_events_1_data["to_calendar_uid"],
                "text": self.calendar_2_events_1_data["text"],
                "datetime": self.calendar_2_events_1_data["datetime"].isoformat(),
            },
        ])

    def test_list_calendar_events_with_wrong_user(self):
        resp = self.client.get(
            url_for("api.list_calendar_transactions", events_id=self.calendar_1.uid),
            headers=self.get_auth_headers(self.user_2_credentials),
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {
            'code': 404,
            'type': 'NOT_FOUND',
            'message': ANY
        })

    def test_unauthorized(self):
        resp = self.client.get(
            url_for("api.list_calendar_events", wallet_id=self.calendar_1.uid)
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {
            'code': 401,
            'type': 'NOT_AUTHORIZED',
            'message': ANY
        })