from discord.ext import commands
from cogs.tts import gen_speech
from cogs.nightcoreify import nightcoreify
from env import TEMP_DIR
from cogs.configuration import count_db, limit_safe, bot_author
import tempfile, discord, asyncio, os, time


async def fn_join(ctx):
    active_client = None
    member_voice = ctx.author.voice

    errors = {
        "UserVoiceIsNone": "You can't ask me to join a voice channel if you're just... not in one!",
    }

    if member_voice is None:  # checking voice state
        await ctx.send(errors["UserVoiceIsNone"])
        return

    for client in ctx.bot.voice_clients:
        if client.channel == member_voice.channel:
            active_client = client
            break

    if active_client is None:
        channel = member_voice.channel
        active_client = await channel.connect()

    return active_client


def add_count(args):
    count = count_db.find_one(name="count")

    try:
        if type(count["total"]) is int:
            count = count["total"]
    except:
        pass

    if count is None:
        count = 0

    count_db.upsert(dict(name="count", total=int(count + len(args))), ["name"])


def setup(bot):
    bot.add_cog(Voice(bot))

async def play(bot, active_client, source, ctx):
    def after(error):
        async def timeout():
            inactive_time = 0
            while active_client.is_playing() is False and inactive_time != 900:
                inactive_time += 1
                await asyncio.sleep(1)
            
            if inactive_time == 900: # 15 minute timeout seems acceptable, will ponder as the bot runs
                await active_client.disconnect()
        
        fut = asyncio.run_coroutine_threadsafe(timeout(), bot.loop)

        try:
            fut.result()
        except Exception as e:
            print(e)

    # not incredibly elegant, but works
    active_client.play(source, after=after)
    await asyncio.sleep(0.1)

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["speak"])
    @commands.check(limit_safe)
    async def tts(self, ctx, *, args):
        active_client = await fn_join(ctx)

        to_delete = None
        source = None

        # so she doesn't do messy things with files and clients that don't exist
        if active_client is None or active_client.is_playing():
            return

        with tempfile.NamedTemporaryFile(suffix=".ogg", dir=TEMP_DIR) as t:
            t.write(gen_speech("Mizuki", args))
            t.seek(0)
            source = await discord.FFmpegOpusAudio.from_probe(t.name)

            await play(self.bot, active_client, source, ctx)
            add_count(args)

    @commands.command()
    @commands.check(limit_safe)
    async def ssml(self, ctx, *, args):
        active_client = await fn_join(ctx)

        to_delete = None
        source = None

        if active_client is None or active_client.is_playing():
            return

        with tempfile.NamedTemporaryFile(suffix=".ogg", dir=TEMP_DIR) as t:
            t.write(gen_speech("Mizuki", args, TextType="ssml"))
            t.seek(0)
            source = await discord.FFmpegOpusAudio.from_probe(t.name)

            await play(self.bot, active_client, source, ctx)
            add_count(args)

    @commands.command(aliases=["nc", "nightcore"])
    async def nightcoreify(self, ctx, *args):
        general_usage = (
            "usage: `nightcoreify <rate> <link>. rate can be any float between 1 and 2."
        )
        active_client = await fn_join(ctx)

        if active_client is None or active_client.is_playing():
            return

        if len(args) < 2:
            await ctx.send(general_usage)
            return

        try:
            float(args[0])
        except:
            await ctx.send(general_usage)
            return

        if float(args[0]) <= 0 or float(args[0]) > 100:
            await ctx.send("Rate must be such that 0 < x <= 100.")
            return

        try:
            source = nightcoreify(args[0], args[1].strip("<").rstrip(">"))
        except:
            await ctx.send(
                "Something went wrong! Are you sure you provided a valid link?"
            )
            return

        await play(self.bot, active_client, source[0], ctx)
        # okay, maybe not elegant at all
        os.remove(source[1])

    @commands.command()
    async def stop(self, ctx):
        user = ctx.author
        active_client = None

        for client in ctx.bot.voice_clients:
            if client.channel == user.voice.channel:
                active_client = client
                break

        if active_client is None:
            return

        active_client.stop()

    @commands.command()
    async def leave(self, ctx):
        user = ctx.author
        active_client = None

        for client in ctx.bot.voice_clients:
            if client.channel == user.voice.channel:
                active_client = client
                break

        if active_client is None:
            return

        await active_client.disconnect()

    @commands.command()
    async def count(self, ctx):
        count_var = count_db.find_one(name="count")
        if count_var is None:
            await ctx.send("No count to keep track of!")
            return

        await ctx.send(f"The current character count is {count_var['total']}.")

    @commands.command()
    @commands.check(bot_author)
    async def reset_character_count(self, ctx, arg):
        previous_count_var = count_db.find_one(name="count")

        if previous_count_var is None:
            await ctx.send("No count to keep track of!")
            return

        try:
            int_arg = int(arg)
        except:
            await ctx.send("Can't convert argument to integer! Try again.")
            return

        previous_count_var = previous_count_var["total"]

        count_db.upsert(dict(name="count", total=int_arg), ["name"])
        await ctx.send(
            f"Total was previously {previous_count_var}. Has been updated to {int_arg}."
        )
