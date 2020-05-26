from mattermostdriver import Driver
from coffeebot.logger import logger
from coffeebot import config, database, utils


def create_driver():
    logger.info("Creating Mattermost Driver...")
    driver_options = {
        'url': config.URL,
        'login_id': config.USERNAME,
        'password': config.PASSWORD,
        'port': config.PORT
    }
    return Driver(driver_options)


def authenticate(driver):
    logger.info("Authenticating...")
    driver.login()
    driver.users.get_user('me')
    logger.info("Successfully authenticated.")


def get_members(driver):
    logger.info("Retrieving Coffee Buddies participants...")
    members = utils.get_channel_members(
        driver, config.TEAM_NAME, config.CHANNEL_NAME)
    logger.info("Successfully retrieved Coffee Buddies participants.")
    return members


def prepare_db(session, members):
    logger.info("Preparing participants database...")
    utils.create_users(session, members)
    utils.create_pairs(session, members)
    logger.info("Succesfully prepared participants database.")


def pair(session, driver, members):
    logger.info("Pairing Coffee Buddies participants...")
    pairs = utils.get_pairs(session, members)
    logger.debug(pairs)
    logger.info("Successfully paired Coffee Buddies participants.")
    logger.info("Messaging paired Coffee Buddies participants...")
    utils.message_pairs(driver, pairs)
    logger.info("Successfully messaged paired Coffee Buddies participants.")


def main():
    session = database.init_session()
    driver = create_driver()
    authenticate(driver)
    members = get_members(driver)
    logger.debug(members)
    prepare_db(session, members)
    pair(session, driver, members)

if __name__ == '__main__':
    main()
