import random

from sqlalchemy.sql import text

from coffeebot import config, session
from coffeebot.models import User, Pair


def get_channel(driver, team_name, channel_name):
    """
    Retrieve a channel given a team and channel name.
    Returns the JSON response from the Mattermost API.
    """
    response = driver.channels.get_channel_by_name_and_team_name(
        team_name, channel_name)
    return response


def get_channel_members(driver, team_name, channel_name):
    """
    Retrieve all of the members from a channel given a team and channel name.
    Returns a list of user IDs sorted alphabetically.
    """
    channel = get_channel(driver, team_name, channel_name)
    channel_id = channel['id']

    # By default, the Mattermost API will return only 60 members. Set this to
    # an amount that is at least the number of members in the channel to get
    # all members
    params = {
        'per_page': '10000'
    }
    response = driver.channels.get_channel_members(channel_id, params=params)

    bot = driver.users.get_user('me')
    bot_id = bot['id']

    # Return all of the user IDs excluding the bot's user ID (don't want to
    # count the bot as a user in pairings)
    members = [
        member['user_id'] for member in response if (
            member['user_id'] != bot_id)]

    # Sort the member list alphabetically so that when we create pairs in the
    # database using the list, we won't create duplicate pairs (A <-> B is the
    # same as B <-> A)
    members.sort()

    return members


def create_users(members):
    """
    Create a User object in the database representing each Mattermost user
    given a list of current users in the channel.
    """
    # Set only the users that exist in the input list as active
    session.query(User).update({
        'active': False})
    session.query(User).filter(User.user_id.in_(members)).update({
        'active': True
    }, synchronize_session='fetch')

    for member in members:
        user = session.query(User).filter(User.user_id == member).all()

        if not user:
            user = User(user_id=member, active=True)
            session.add(user)

    session.commit()


def create_pairs(members):
    """
    Create a Pair object in the database representing a potential pairing
    between two Mattermost users given a list of current users in the channel.
    """
    # In order to prevent duplicate pairings (A <-> B is the same as B <-> A),
    # the input list must be alphabetically sorted
    # We iterate over the list of members similar to a selection sort in order
    # create every possible pairing
    for i, first_user in enumerate(members):
        for second_user in members[i + 1:]:
            pair = session.query(Pair).filter(
                Pair.first_user_id == first_user,
                Pair.second_user_id == second_user).all()

            if not pair:
                new_pair = Pair(
                    first_user_id=first_user,
                    second_user_id=second_user,
                    count=0)
                session.add(new_pair)

    session.commit()


def get_pair(members):
    """
    Generate one pair of users from a list of members depending on the
    frequencies of each user's previous pairings.
    """
    member = members[0]

    # Select a single user that is currently active in the channel, has not
    # been paired with another member in this session yet, and has the lowest
    # frequency of previous pairings with the current user
    sql = text("""
        SELECT paired_member
        FROM (
            SELECT p.first_user_id as paired_member, p.count
            FROM pairs p
            JOIN users u ON u.user_id = p.first_user_id
            WHERE p.second_user_id = :member
            AND u.is_paired = 0
            AND u.active = 1
            UNION
            SELECT p.second_user_id as paired_member, p.count
            FROM pairs p
            JOIN users u ON u.user_id = p.second_user_id
            WHERE p.first_user_id = :member
            AND u.is_paired = 0
            AND u.active = 1
        )
        ORDER BY count ASC
        LIMIT 1
    """)

    result = session.execute(sql, {'member': member})
    paired_member = result.first()[0]

    # Increase the historical number of times this pair has been paired up
    # before
    sql = text("""
        UPDATE pairs
        SET count = count + 1
        WHERE (first_user_id = :first_member
            AND second_user_id = :second_member)
        OR (first_user_id = :second_member
            AND second_user_id = :first_member)
    """)

    session.execute(
        sql, {'first_member': member, 'second_member': paired_member})

    # Mark both users as is_paired so that on the next pairing, we won't try to
    # pair either user with a different user
    sql = text("""
        UPDATE users
        SET is_paired = 1
        WHERE user_id = :first_member
        OR user_id = :second_member
    """)

    session.execute(
        sql, {'first_member': member, 'second_member': paired_member})
    session.commit()

    members.remove(member)
    members.remove(paired_member)

    return member, paired_member


def get_pairs(members):
    """
    Pair up all users from a list of members depending on the frequencies of
    each user's previous pairings.
    Returns a list of tuples of user IDs.
    """
    pairs = []
    unmatched = None
    if len(members) < 2:
        return pairs, unmatched

    # In the case of an odd number of members, the user that is sequentially
    # last in the input list will have a lower chance of getting paired. In
    # order to make it fair, we shuffle the list so that everyone has an equal
    # chance of not getting paired
    random.shuffle(members)

    while len(members) > 1:
        pairs.append(get_pair(members))

    if len(members) == 1:
        unmatched = members[0]

    # Reset the is_paired flag for each user in preparation for the next time
    # users get paired
    sql = text("""
        UPDATE users
        SET is_paired = 0
    """)

    session.execute(sql)
    session.commit()

    return pairs, unmatched


def message_channel(driver, team_name, channel_name):
    """
    Send a channel message to channel to notifying members of upcoming
    pairing.
    Returns the JSON response from the Mattermost API.
    """
    channel = get_channel(driver, team_name, channel_name)
    channel_id = channel['id']

    message = config.CHANNEL_MESSAGE
    message_options = {
        "channel_id": channel_id,
        "message": message
    }

    response = driver.posts.create_post(message_options)
    return response


def message_pair(driver, pair):
    """
    Send a group message to both users in a pair notifying them of their
    pairing.
    Returns the JSON response from the Mattermost API.
    """
    user_list = list(pair)
    channel = driver.channels.create_group_message_channel(user_list)
    channel_id = channel['id']

    message = config.PAIR_MESSAGE
    message_options = {
        "channel_id": channel_id,
        "message": message
    }

    response = driver.posts.create_post(message_options)
    return response


def message_unmatched(driver, unmatched):
    """
    Send a direct message to the unmatched user notifying them of others.
    Returns the JSON response from the Mattermost API.
    """
    if not unmatched:
        return

    bot_id = driver.users.get_user('me')['id']
    channel = driver.channels.create_direct_message_channel([bot_id, unmatched])
    channel_id = channel['id']

    message = config.UNMATCHED_MESSAGE
    message_options = {
        "channel_id": channel_id,
        "message": message
    }

    response = driver.posts.create_post(message_options)
    return response


def message_pairs(driver, pairs, unmatched):
    """
    Send a group message to each pair of users notifying them of their pairing.
    """
    for pair in pairs:
        message_pair(driver, pair)

    if unmatched:
        message_unmatched(driver, unmatched)


def get_channels(driver):
    """
    Retrieve all channels of any teams that the bot has been added to.
    Returns a generator of tuples with team and channel names.
    """
    # Iterate all teams the bot has been added to
    teams = driver.teams.get_user_teams(user_id='me')
    for team in teams:

        # Iterate all channels this bot has been added to
        channels = driver.channels.get_channels_for_user(user_id='me', team_id=team['id'])
        for channel in channels:

            # Only public and private channels
            if channel['type'] not in ('O', 'P'):
                continue

            # Skip default channels
            if config.SKIP_TOWN_SQUARE and channel['name'] == 'town-square':
                continue
            if config.SKIP_OFF_TOPIC and channel['name'] == 'off-topic':
                continue

            '''
            # Retrieve all members
            members = set()
            page_idx = 0
            # - Iterate
            while True:
                params = {'page': page_idx}
                memberships = driver.channels.get_channel_members(channel['id'], params=params)
                if not memberships:
                    break
                for membership in memberships:
                    assert membership['channel_id'] == channel['id']
                    members.add(membership['user_id'])
                page_idx += 1

            # Exclude the bot itself
            assert bot_user['id'] in members
            members.remove(bot_user['id'])
            '''

            yield team['name'], channel['name']
