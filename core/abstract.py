from settings import db
from bson import ObjectId
from utils import get_dict
from datetime import datetime


class AbstractModel:
    def __init__(self, _id=None, **attributes):
        if _id:
            self._id = ObjectId(_id)
        for attribute_name, value in attributes.items():
            setattr(self, attribute_name, value)
        self.created = self.modified = datetime.now()

    @classmethod
    def get_collection(cls):
        return db[cls._collection_name] if cls._collection_name else None

    @property
    def exclude_fields(self):
        return []

    def to_representation(self):
        data = self.__dict__
        for field in self.exclude_fields:
            try:
                data.pop(field)
            except KeyError:
                continue

        return data

    @classmethod
    def find(cls, **filter_values):
        collection = cls.get_collection()
        if not collection:
            return []

        instance_list = []
        for raw_o in collection.find(filter_values):
            raw_o.update(dict(_id=str(raw_o.get('_id'))))

            instance = cls()
            for key, item in raw_o.items():
                setattr(instance, key, item)
            instance_list.append(instance)

        return instance_list

    @classmethod
    def find_one(cls, **filter_values):
        instance_list = cls.find(**filter_values)

        try:
            instance = instance_list[0]
        except IndexError:
            instance = None

        return instance

    def validate(self):
        errors = {}

        for validate_function in self.validators:
            try:
                validate_function()
            except Exception as err:
                err = get_dict(err)
                for key, value in err.items():
                    errors.setdefault(key, [])
                    errors[key].extend(value)

        return errors

    def save(self, **new_values):
        self.modified = datetime.now()
        collection = self.get_collection()
        if not collection:
            return None, dict(__all__='collection not found')

        try:
            if hasattr(self, '_id'):
                _id = ObjectId(self._id)
                if new_values:
                    updating_values = new_values
                else:
                    updating_values = get_dict(self)
                updating_values.pop('_id')
                collection.update_one(dict(_id=_id), {'$set': updating_values})
            else:
                _id = collection.insert(self.__dict__)
        except Exception as err:
            return None, get_dict(err)

        instance = self.__class__.find_one(_id=_id)

        return instance, {}
