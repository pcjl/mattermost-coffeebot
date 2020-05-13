import os


__DIR__ = os.path.dirname(__file__)

if os.getenv('COFFEEBOT_DATABASE_URI'):
    DATABASE_URI = os.getenv('COFFEEBOT_DATABASE_URI')
else:
    DATABASE_URI = 'sqlite:////' + __DIR__ + '/../' + \
        os.getenv('COFFEEBOT_DATABASE_FILENAME')

DEBUG = int(os.getenv('COFFEEBOT_DEBUG', 0))

URL = os.getenv('COFFEEBOT_MATTERMOST_URL')
PORT = int(os.getenv('COFFEEBOT_MATTERMOST_PORT'))

USERNAME = os.getenv('COFFEEBOT_MATTERMOST_USERNAME')
PASSWORD = os.getenv('COFFEEBOT_MATTERMOST_PASSWORD')

TEAM_NAME = os.getenv('COFFEEBOT_MATTERMOST_TEAM')
CHANNEL_NAME = os.getenv('COFFEEBOT_MATTERMOST_CHANNEL')

MESSAGE = """
You have been matched to meet up! Please respond with your availabilities :)
"""
