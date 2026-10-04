"""Discord bot that DMs you a different sheep fact every day.

python bot.py          stay running and send a fact daily at SEND_TIME
python bot.py --once   send one fact now and exit
python bot.py --daily  send one fact if it's past SEND_TIME and none was sent
                       today, then exit (used by GitHub Actions)
"""

import datetime
import json
import os
import random
import asyncio
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks
from dotenv import load_dotenv

HERE = Path(__file__).parent
load_dotenv(HERE / ".env")

TOKEN = os.environ["DISCORD_TOKEN"]
USER_ID = int(os.environ["DISCORD_USER_ID"])
TZ = ZoneInfo(os.getenv("TIMEZONE", "America/Los_Angeles"))
SEND_AT = datetime.time.fromisoformat(os.getenv("SEND_TIME", "09:00")).replace(tzinfo=TZ)

FACTS_FILE = HERE / "facts.txt"
STATE_FILE = HERE / "state.json"


def load_state():
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}


def today():
    return datetime.datetime.now(TZ).date().isoformat()


def is_due():
    now = datetime.datetime.now(TZ)
    return now.time() >= SEND_AT.replace(tzinfo=None) and load_state().get("last_sent") != today()


def next_fact():
    """Pop a fact from a shuffled queue so none repeat until all have been sent."""
    facts = [line.strip() for line in FACTS_FILE.read_text().splitlines() if line.strip()]
    state = load_state()
    # Drop anything that was removed from facts.txt since the queue was built.
    queue = [f for f in state.get("queue", []) if f in facts]
    if not queue:
        queue = facts[:]
        random.shuffle(queue)
    fact = queue.pop()
    STATE_FILE.write_text(json.dumps({"last_sent": today(), "queue": queue}, indent=2))
    return fact


async def send_fact(client):
    user = await client.fetch_user(USER_ID)
    await user.send(f"🐑 **Sheep fact of the day**\n{next_fact()}")
    print(f"Sent a fact to {user}.")


async def send_once():
    # Only REST calls are needed to send a DM, so skip the gateway connection.
    async with discord.Client(intents=discord.Intents.default()) as client:
        await client.login(TOKEN)
        await send_fact(client)


class SheepBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())

    async def setup_hook(self):
        self.daily_fact.start()

    async def on_ready(self):
        print(f"Logged in as {self.user}. Sending facts daily at {SEND_AT.strftime('%H:%M')} {TZ}.")

    @tasks.loop(time=SEND_AT)
    async def daily_fact(self):
        await send_fact(self)

    @daily_fact.before_loop
    async def before_daily_fact(self):
        await self.wait_until_ready()


if __name__ == "__main__":
    if "--daily" in sys.argv:
        if is_due():
            asyncio.run(send_once())
        else:
            print("Not sending: already sent today, or it's before SEND_TIME.")
    elif "--once" in sys.argv or "--test" in sys.argv:
        asyncio.run(send_once())
    else:
        SheepBot().run(TOKEN)
