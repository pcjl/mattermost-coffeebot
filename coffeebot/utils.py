import random

from sqlalchemy import text

from coffeebot import config, session
from coffeebot.models import User, Pair


def get_channel(driver, team_name, channel_name):
    """
    Retrieve a channel given a team and channel name.
    """
    response = driver.channels.get_channel_by_name_and_team_name(
        team_name, channel_name)
    return response


def get_channel_members(driver, team_name, channel_name):
    """
    Retrieve all members from a channel.
    Returns a sorted list of user IDs.
    """
    channel = get_channel(driver, team_name, channel_name)
    channel_id = channel['id']

    params = {'per_page': '10000'}
    response = driver.channels.get_channel_members(channel_id, params=params)

    bot = driver.users.get_user('me')
    bot_id = bot['id']

    members = [
        member['user_id'] for member in response
        if member['user_id'] != bot_id
    ]
    members.sort()

    return members


def create_users(members):
    """
    Sync users in the database with the current channel members.
    """
    session.query(User).update({'active': False})
    session.query(User).filter(User.user_id.in_(members)).update(
        {'active': True}, synchronize_session='fetch'
    )

    for member in members:
        user = session.query(User).filter(User.user_id == member).first()
        if not user:
            session.add(User(user_id=member, active=True))

    session.commit()


def create_pairs(members):
    """
    Create all possible Pair records for current members.
    """
    for i, first_user in enumerate(members):
        for second_user in members[i + 1:]:
            pair = session.query(Pair).filter(
                Pair.first_user_id == first_user,
                Pair.second_user_id == second_user
            ).first()

            if not pair:
                session.add(Pair(
                    first_user_id=first_user,
                    second_user_id=second_user,
                    count=0
                ))

    session.commit()


def get_pair(members):
    """
    Generate one pair from the members list based on lowest pairing frequency.
    """
    member = members[0]

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

    session.execute(
        text("""
            UPDATE pairs
            SET count = count + 1
            WHERE (first_user_id = :first AND second_user_id = :second)
            OR (first_user_id = :second AND second_user_id = :first)
        """),
        {'first': member, 'second': paired_member}
    )

    session.execute(
        text("""
            UPDATE users
            SET is_paired = 1
            WHERE user_id = :first OR user_id = :second
        """),
        {'first': member, 'second': paired_member}
    )

    session.commit()

    members.remove(member)
    members.remove(paired_member)

    return (member, paired_member)


def get_pairs(members):
    """
    Pair up all members and return list of tuples.
    """
    random.shuffle(members)

    pairs = []
    while len(members) > 1:
        pairs.append(get_pair(members))

    session.execute(text("UPDATE users SET is_paired = 0"))
    session.commit()

    return pairs


def message_pair(driver, pair):
    """
    Send a group message to a pair of users.
    """
    channel = driver.channels.create_group_message_channel(list(pair))
    channel_id = channel['id']

    response = driver.posts.create_post({
        "channel_id": channel_id,
        "message": config.MESSAGE
    })
    return response


def message_pairs(driver, pairs):
    """
    Send group messages to all pairs.
    """
    for pair in pairs:
        message_pair(driver, pair)