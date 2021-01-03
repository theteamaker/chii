from discord.ext import commands
from cogs.tts import gen_speech
from env import TEMP_DIR
import tempfile, discord, asyncio

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
    
    active_client.stop()

    return active_client

def setup(bot):
    bot.add_cog(Voice(bot))

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['speak'])
    async def tts(self, ctx, *, args):
        active_client = await fn_join(ctx)

        to_delete = None
        source = None
        
        if active_client is None:                   # so she doesn't do messy things with files and clients that don't exist
            return

        with tempfile.NamedTemporaryFile(suffix='.ogg', dir=TEMP_DIR) as t:
            t.write(gen_speech("Mizuki", args))
            t.seek(0)
            source = await discord.FFmpegOpusAudio.from_probe(t.name)

            async def play():
                active_client.play(source)          # not incredibly elegant, but works
                await asyncio.sleep(0.1)
            
            await play()
        
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