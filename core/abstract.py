from settings import db
from bson import ObjectId
from utils import get_dict
from datetime import datetime


class AbstractModel:
    def __init__(self, _id=None):
        if _id:
            self._id = ObjectId(_id)
        self.created = self.modified = datetime.now()

    @classmethod
    def get_collection(cls):
        return db[cls._collection_name]

    @classmethod
    def find(cls, filter_data={}):
        o_list = []
        for o in cls.get_collection().find(filter_data):
            o.update(dict(_id=str(o.get('_id'))))
            o_list.append(o)

        return o_list

    def validate(self):
        errors = {}

        try:
            for validate_function in self.validators:
                validate_function()
        except Exception as err:
            err = get_dict(err)
            for key, value in err.items():
                errors.setdefault(key, [])
                errors[key].extend(value)

        return errors

    def save(self, **new_values):
        self.modified = datetime.now()

        try:
            if hasattr(self, '_id'):
                _id = self._id
                if new_values:
                    self.get_collection().update_one(
                        dict(_id=ObjectId(_id)),
                        {'$set': new_values},
                    )
            else:
                self.get_collection().insert(self.__dict__)
        except Exception as err:
            return None, get_dict(err)

        return self, {}
