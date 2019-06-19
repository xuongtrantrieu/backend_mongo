from core.abstract import AbstractModel


class User(AbstractModel):
    _collection_name = 'user'

    def __init__(self, username='', **kwargs):
        super().__init__(**kwargs)
        self.username = username.lower()

    def validate_username(self):
        self._validate_username_format()
        self._validate_username_uniqueness()

    def _validate_username_format(self):
        if not self.username:
            raise ValueError({'username': 'should not be blank'})

    def _validate_username_uniqueness(self):
        if User.find({'username': self.username.lower()}):
            raise ValueError({'username': 'already existed'})

    @property
    def validators(self):
        return [
            self.validate_username
        ]
