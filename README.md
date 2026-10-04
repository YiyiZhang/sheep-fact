# Sheep Fact Bot 🐑

Sends you a direct message on Discord with a different sheep fact every day. It goes through all the facts in `facts.txt` in random order before any fact repeats.

## Setup

1. **Create the bot.** Go to https://discord.com/developers/applications, click **New Application**, open the **Bot** tab, click **Reset Token** and copy the token.
2. **Invite it to a server you're in.** Discord only lets a bot DM you if you share a server with it. Under **OAuth2 → URL Generator**, tick the `bot` scope, open the URL it generates and pick a server (a private server just for you works fine).
3. **Get your user ID.** In Discord, go to Settings → Advanced and turn on **Developer Mode**. Then right-click your name and choose **Copy User ID**.
4. **Configure.** Copy `.env.example` to `.env` and fill in your token and ID. You can also change the timezone and send time there.
5. **Install and test:**
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   .venv/bin/python bot.py --test   # sends one fact right away, then exits
   ```
6. **Run it for real:** `.venv/bin/python bot.py`

## Keeping it running

The bot can only send facts while `bot.py` is running. To get a fact every day, run it on a computer that's always on, such as a Raspberry Pi, a small VPS, or a free host like fly.io or Railway.

## Adding facts

Write one fact per line in `facts.txt`. The bot picks up new facts the next time its current list runs out.
