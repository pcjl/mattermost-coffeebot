# Mattermost Coffeebot

*Mattermost Coffeebot* is a bot written in Python that interacts with the [Mattermost API](https://api.mattermost.com/) using [`mattermostdriver`](https://github.com/Vaelor/python-mattermost-driver) and pairs users in your Mattermost team on a regular basis to meet each other.

The bot will take users within a specific channel and message random pairs to meet up. The channel and frequency of these pairings can be configured.

### Features

- Written in Python
- Uses the [Mattermost API](https://api.mattermost.com/)
- Automatically pairs Mattermost users
- Uses past pairing data to pair people with people they have not been paired with before
- Configurable pairing times (by modifying cronjob)

### Future Features

- Follow-ups to make sure paired users actually met
- Better deployment process (deployment script)

### Technologies Used

- Python 3.4+
- SQLite
- Docker

### Deployment

As of right now, the project is deployed by manually cloning the repository onto a server (such as an AWS EC2 instance), installing the dependencies, creating the environment variables, and setting up a cronjob.

The database is only used for storing previous pairings in order to increase the probability of pairing each user with another user they haven't been paired with before. Should the database be lost, any previous data will be gone, but the bot will still function, just without any data on previous pairings.

Due to this, if you do use SQLite for your database, it is not ideal to use the Docker container on production because your database will be gone if your container gets stopped. However, theoretically, if you use a database hosted on a separate server or on RDS, it should be safe to use the Docker container.

Here are the current steps to deploying:

1. Create a user that the bot will run as and add it to the rooms it will use to pair people.

2. Clone the repository into a directory

3. Install Python 3.4+, `pip`, and `cron`.
    - On Ubuntu, this can be done by running `sudo apt-get update && apt-get install -y -qq cron python3 python3-pip`

4. Install the Python packages by running `sudo pip3 install -r requirements.txt` in the directory

5. Create a `.env` file in the directory with all of your credentials/settings following the same format as the `example.env` file supplied

6. Set up a cronjob with your frequency following the same format as the `example.crontab` file supplied
    - This can be done by running `crontab -e` and adding the cronjob there

### Development

In order to set up a local development environment:

*This assumes that you already have Docker installed*

1. Clone the repository into a directory

2. Create a `.env` file in the directory with all of your credentials/settings following the same format as the `example.env` file supplied

3. Create a `crontab` file in the directory with your frequency following the same format as the `example.crontab` file supplied

3. Build the Docker image by running `docker-compose build`

4. Create the Docker container by running `docker-compose up`

5. Run `bash` in the container by running `docker exec -ti <CONTAINERID> bash`

6. Run the command `pair` (or allow the cronjob that was set up to run it)

If you make any changes to the bot, you will have to rebuild the Docker image to apply the changes.

### License

```
MIT License

Copyright (c) 2018 Patrick Liu
Copyright (c) 2019 Gaelan D'costa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
