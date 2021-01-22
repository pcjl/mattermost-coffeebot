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
PORT = int(os.getenv('COFFEEBOT_MATTERMOST_PORT'))

USERNAME = os.getenv('COFFEEBOT_MATTERMOST_USERNAME')
PASSWORD = os.getenv('COFFEEBOT_MATTERMOST_PASSWORD')
TOKEN = os.getenv('COFFEEBOT_MATTERMOST_TOKEN')

SKIP_TOWN_SQUARE = bool(os.getenv('COFFEEBOT_MATTERMOST_SKIP_TOWN_SQUARE'))
SKIP_OFF_TOPIC = bool(os.getenv('COFFEEBOT_MATTERMOST_SKIP_OFF_TOPIC'))

CHANNEL_MESSAGE = """
Here we go with another round of paring you up. Stay tuned until the lottery
has drawn your Coffee Buddy.
"""

PAIR_MESSAGE = """
You have been matched to meet up! Please respond with your availabilities :)
"""

UNMATCHED_MESSAGE = """
Bad luck in lottery. All other Coffee Buddies have already been paired.
Why not reaching out to someone you prefer?
"""
