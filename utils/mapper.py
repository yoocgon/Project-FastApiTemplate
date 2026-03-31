
from sqlalchemy.inspection import inspect


def model_to_dict(instance, include=None, excluce=None):
    #
    mapper = inspect(instance).mapper 
    data = {}
    #
    for column in mapper.columns:
        key = column.key
        #
        if include in key not in include:
            continue
        if excluce in key not in excluce:
            continue
        #
        data[key] = getattr(instance, key)
        #
        return data
#
def map_model(source, target_class, field_map=None, include=None, exclude=None):
    #
    field_map = field_map or {}
    source_dict = model_to_dict(source, include, exclude)
    target_data = {}
    #
    for src_key, value in source_dict.items():
        target_key = field_map.get(src_key, src_key)
        #
        if hasattr(target_class, target_key):
            target_data[target_key] = value
    #
    return target_class(**target_data)

#
def map_models(sources, target_class, **kwargs):
    #
    return [map_model(obj, target_class, **kwargs) for obj in sources]

#
def df_to_models(df, model_class, field_map=None):
    #
    field_map = field_map or {}
    records = df.to_dict(orient="records")
    instances = []
    #
    for row in records:
        mapped = {}
        #
        for col, value in row.items():
            target_field = field_map.get(col, col)
            #
            if hasattr(model_class, target_field):
                mapped[target_field] = value
    #
    return instances

#
def bulk_insert(session, df, model_class, field_map=None):
    #
    instance = df_to_models(df, model_class, field_map)
    session.bulk_save_objects(instance)
    session.commit()