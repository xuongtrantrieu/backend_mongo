import flask


def make_response(*data, errors={}, meta={}, status_code=200):
    cleaned_data = []
    for d in data:
        if not isinstance(d, dict):
            d = d.__dict__

        if '_id' in d.keys():
            d['_id'] = str(d['_id'])

        cleaned_data.append(d)

    response_data = dict(
        data=[d.__dict__ if not isinstance(d, dict) else d for d in data],
        errors=errors,
        meta=meta,
    )

    return flask.jsonify(response_data), status_code


def get_dict(err):
    errors = {}

    for e in err.args:
        if isinstance(e, str):
            errors.setdefault('__all__', [])
            errors['__all__'].append(e)
        elif isinstance(e, dict):
            for key, item in e.items():
                errors.setdefault(key, [])
                errors[key].append(item)

    return errors
