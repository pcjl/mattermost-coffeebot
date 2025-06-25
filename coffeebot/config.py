import os

from dotenv import load_dotenv


__DIR__ = os.path.dirname(__file__)
load_dotenv(dotenv_path=__DIR__ + '/../.env')

if os.getenv('COFFEEBOT_DATABASE_URI') is not None:
    DATABASE_URI = os.getenv('COFFEEBOT_DATABASE_URI')
else:
    DATABASE_URI = 'sqlite:////' + __DIR__ + '/../' + \
        os.getenv('COFFEEBOT_DATABASE_FILENAME')

URL = os.getenv('COFFEEBOT_MATTERMOST_URL')

TOKEN = os.getenv('COFFEEBOT_MATTERMOST_TOKEN')

TEAM_NAME = os.getenv('COFFEEBOT_MATTERMOST_TEAM')
CHANNEL_NAME = os.getenv('COFFEEBOT_MATTERMOST_CHANNEL')

MESSAGE = """
You have been matched to meet up for a virtual coffee! Please respond with your availabilities and set yourselves up a call :)
"""
