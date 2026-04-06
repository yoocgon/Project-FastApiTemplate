from utils.mapper import map_model, df_to_models


class Mapper:
    #
    def __init__(self, field_map=None):
        #
        self.field_map = field_map or {}
    #
    def to_model(self, source, target_class):
        return map_model(source, target_class, self.field_map)
    
    #
    def df_to_models(self, df, model_class):
        return df_to_models(df, model_class, self.field_map)
            
