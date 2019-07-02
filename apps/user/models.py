from core.abstract import AbstractModel
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request


class User(AbstractModel):
    _collection_name = 'user'

    def __init__(self, email='', **kwargs):
        self.password = ''
        self.credentials = {}
        super().__init__(**kwargs)
        self.email = email.lower()

    @property
    def exclude_fields(self):
        return ['password', 'credentials']

    def set_password(self, password):
        self.password = generate_password_hash(password)
        return self

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def validate_email(self):
        self._validate_email_format()
        self._validate_email_uniqueness()

    def validate_password(self):
        password_is_empty = check_password_hash(self.password, '')
        if password_is_empty:
            raise ValueError(dict(password='should not be blank'))

    def _validate_email_format(self):
        if not self.email:
            raise ValueError(dict(email='should not be blank'))

    def _validate_email_uniqueness(self):
        if User.find(email=self.email.lower()):
            raise ValueError(dict(email='already existed'))

    @property
    def validators(self):
        return [
            self.validate_email,
            self.validate_password,
        ]
