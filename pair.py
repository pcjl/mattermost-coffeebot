from mattermostdriver import Driver

from coffeebot import config, utils


def main():
    print("Creating Mattermost Driver...")
    driver_options = {
        'url': config.URL,
        'login_id': config.USERNAME,
        'password': config.PASSWORD,
        'token': config.TOKEN,
        'port': config.PORT
    }
    driver = Driver(driver_options)

    print("Authenticating...")
    driver.login()
    driver.users.get_user('me')
    print("Successfully authenticated.")

    print("Retrieving Coffee Buddies participants...")
    team_name = config.TEAM_NAME
    channel_name = config.CHANNEL_NAME
    members = utils.get_channel_members(driver, team_name, channel_name)
    print("Successfully retrieved Coffee Buddies participants.")

    print("Preparing participants database...")
    utils.create_users(members)
    utils.create_pairs(members)
    print("Succesfully prepared participants database.")

    print("Pairing Coffee Buddies participants...")
    pairs = utils.get_pairs(members)
    print("Successfully paired Coffee Buddies participants.")

    print("Messaging paired Coffee Buddies participants...")
    utils.message_pairs(driver, pairs)
    print("Successfully messaged paired Coffee Buddies participants.")


if __name__ == '__main__':
    main()
