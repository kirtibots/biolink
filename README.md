# Bio Link Cleaner Bot

A Pyrogram + MongoDB Telegram group bot based on the supplied screenshots.

## Features
- `/start` menu with Add, Owner, About and Help buttons.
- `/ping` latency check.
- `/stats` bot statistics.
- Checks users' Telegram bio for links.
- Deletes messages from users whose bio contains a link.
- Warns the user with a mention.
- Mutes the user after `WARN_LIMIT` warnings.
- Admin commands: `/auth`, `/unauth`, `/authusers`, `/clearauthusers`, `/resetwarn`.
- MongoDB storage for authorized users, warnings and statistics.
- Environment variables for support/update/owner buttons.

## Telegram permissions
Add the bot to your group and promote it to admin with at least:
- Delete messages
- Restrict users

The bot does not moderate group administrators.

## Deploy
1. Create a MongoDB database.
2. Set all required variables from `.env.example`.
3. Install:
   `pip install -r requirements.txt`
4. Run:
   `python bot.py`

For Heroku/Render-style workers, use the included `Procfile`.

## Important
The screenshots do not contain the original source code or the real support/owner URLs, so those values are configurable through environment variables.

## Startup logger
On startup the worker prints a screenshot-style success logger with bot name, plugin count, Pyrogram version, Python version and powered-by text. Configure these with `PLUGIN_COUNT`, `LOGGER_BOT_NAME` and `LOGGER_POWERED_BY`.

## Heroku deployment
- The included `Procfile` runs the bot as a worker.
- `runtime.txt` pins Python 3.11.9.
- Add the required Config Vars: `API_ID`, `API_HASH`, `BOT_TOKEN`, `MONGO_URI`.
- Add optional variables from `.env.example` if you want custom buttons/logger text.
- Scale the `worker` process to 1.

## Railway deployment
- The included `Dockerfile` automatically builds the bot on Railway.
- `railway.toml` configures the Docker deployment and restart policy.
- Add the same required environment variables in Railway Variables.
- Deploy the repository/ZIP contents; Railway will start `python bot.py`.

### Required variables
`API_ID`, `API_HASH`, `BOT_TOKEN`, `MONGO_URI`

### Optional variables
`BOT_USERNAME`, `SUPPORT_URL`, `UPDATE_URL`, `OWNER_URL`, `PROMO_URL`, `WARN_LIMIT`, `MUTE_MINUTES`, `PLUGIN_COUNT`, `LOGGER_BOT_NAME`, `LOGGER_POWERED_BY`
