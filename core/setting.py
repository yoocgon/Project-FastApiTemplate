
from models.settings import Settings


settings: Settings = None


def init():
    #
    global settings
    #
    settings = Settings()
    