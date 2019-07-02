import flask


def make_response(*data, message='', errors={}, meta={}, status_code=200):
    cleaned_data = []
    for d in data:
        if d is None:
            continue

        if hasattr(d, 'to_representation') and callable(d.to_representation):
            d = d.to_representation()
        elif hasattr(d, '__dict__'):
            d = d.__dict__
        else:
            pass

        if isinstance(d, dict) and '_id' in d.keys():
            d['_id'] = str(d['_id'])

        cleaned_data.append(d)

    if isinstance(errors, Exception):
        errors = get_dict(errors)

    response_data = dict(
        data=cleaned_data,
        message=str(message),
        errors=errors,
        meta=meta,
    )

    return flask.jsonify(response_data), status_code


def get_dict(o):
    result = {}

    if isinstance(o, Exception):
        for e in o.args:
            if isinstance(e, str):
                result.setdefault('__all__', [])
                result['__all__'].append(e)
            elif isinstance(e, dict):
                for key, item in e.items():
                    result.setdefault(key, [])
                    result[key].append(item)
    else:
        result = o.__dict__ if hasattr(o, '__dict__') else {}

    return result
