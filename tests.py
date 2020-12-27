from unittest import TestCase
from unittest.mock import patch, Mock

from flask_bcrypt import generate_password_hash



@patch('prukladne7.auth.Session')
class TestAuthenticate(TestCase):
    def setUp(self):
        app.config['SECRET_KEY'] = 'super-secret'
        self.admin_username = "admin-aec8084845b41a6952d46cbaa1c9b798659487ffd133796d95d05ba45d9096c2"
        self.admin_password = app.config['SECRET_KEY']
        self.user_username = "my-user"
        self.user_password = "my-password"
        self.hashed_user_password = generate_password_hash(self.user_password)

    def test_authenticate_admin(self, _Session):
        identity = authenticate(self.admin_username, self.admin_password)
        self.assertIsInstance(identity, AdminUserIdentity)

    def test_authenticate_admin_failed(self, Session):
        Session().query().filter_by().one.return_value = Mock(
            password=self.hashed_user_password
        )
        identity = authenticate(self.admin_username, "invalid_password")
        self.assertIsNone(identity)

    def test_authenticate_user(self, Session):
        Session().query().filter_by().one.return_value = Mock(
            password=self.hashed_user_password
        )
        identity = authenticate(self.user_username, self.user_password)
        self.assertIsInstance(identity, UserModelIdentity)

    def test_authenticate_user_failed(self, Session):
        Session().query().filter_by().one.return_value = Mock(
            password=self.hashed_user_password
        )
        identity = authenticate(self.user_username, "invalid_password")
        self.assertIsNone(identity)