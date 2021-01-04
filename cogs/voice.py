from discord.ext import commands
from cogs.tts import gen_speech
from cogs.nightcoreify import nightcoreify
from env import TEMP_DIR
from cogs.configuration import count_db, limit_safe, bot_author
import tempfile, discord, asyncio, os

async def fn_join(ctx):
    active_client = None
    member_voice = ctx.author.voice

    errors = {
        "UserVoiceIsNone": "You can't ask me to join a voice channel if you're just... not in one!",
    }

    if member_voice is None:                        # checking voice state
        await ctx.send(
            errors["UserVoiceIsNone"]
        )
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

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['speak'])
    @commands.check(limit_safe)
    async def tts(self, ctx, *, args):
        active_client = await fn_join(ctx)
        
        to_delete = None
        source = None
        
        if active_client is None or active_client.is_playing():                   # so she doesn't do messy things with files and clients that don't exist
            return

        with tempfile.NamedTemporaryFile(suffix='.ogg', dir=TEMP_DIR) as t:
            t.write(gen_speech("Mizuki", args))
            t.seek(0)
            source = await discord.FFmpegOpusAudio.from_probe(t.name)

            async def play():
                active_client.play(source)          # not incredibly elegant, but works
                await asyncio.sleep(0.1)
            
            await play()
            add_count(args)

    @commands.command()
    @commands.check(limit_safe)
    async def ssml(self, ctx, *, args):
        active_client = await fn_join(ctx)

        to_delete = None
        source = None
        
        if active_client is None or active_client.is_playing():
            return

        with tempfile.NamedTemporaryFile(suffix='.ogg', dir=TEMP_DIR) as t:
            t.write(gen_speech("Mizuki", args, TextType="ssml"))
            t.seek(0)
            source = await discord.FFmpegOpusAudio.from_probe(t.name)

            async def play():
                active_client.play(source)          # not incredibly elegant, but works
                await asyncio.sleep(0.1)
            
            await play()
            add_count(args)

    @commands.command(aliases=["nc"])
    async def nightcoreify(self, ctx, *args):
        general_usage = "usage: `nightcoreify <rate> <link>. rate can be any float between 1 and 2."
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
        
        if float(args[0]) < 1 or float(args[0]) > 2:
            await ctx.send("Rate must be any float between 1 and 2.")
            return
        
        try:
            nc = nightcoreify(args[0], args[1])
        except:
            await ctx.send("Something went wrong! Are you sure you provided a valid link?")
            return

        async def play():
            active_client.play(nc[0])           # not incredibly elegant, but works
            await asyncio.sleep(0.1)
        
        await play()
        os.remove(nc[1])                        # okay, maybe not elegant at all
    
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
        await ctx.send(f"Total was previously {previous_count_var}. Has been updated to {int_arg}.")