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

    for team_name, channel_name in utils.get_channels(driver):

        print("Retrieving Coffee Buddies participants for {:s}/{:s}...".format(
            team_name, channel_name
        ))
        utils.message_channel(driver, team_name, channel_name)
        members = utils.get_channel_members(driver, team_name, channel_name)
        print("Successfully retrieved Coffee Buddies participants.")

        print("Preparing participants database...")
        utils.create_users(members)
        utils.create_pairs(members)
        print("Successfully prepared participants database.")

        print("Pairing Coffee Buddies participants...")
        pairs, unmatched = utils.get_pairs(members)
        print("Successfully paired Coffee Buddies participants.")

        print("Messaging paired Coffee Buddies participants...")
        utils.message_pairs(driver, pairs, unmatched)
        print("Successfully messaged paired Coffee Buddies participants.")


if __name__ == '__main__':
    main()
