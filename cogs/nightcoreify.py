from discord.ext import commands
import youtube_dl, tempfile, discord
from env import TEMP_DIR


def nightcoreify(rate, link):
    ydl_opts = {
        "format": "bestaudio",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "opus",
                "preferredquality": "128",
            }
        ],
    }

    with tempfile.NamedTemporaryFile(dir=TEMP_DIR) as t:
        filename = str(t.name) + "_ytdl.opus"
        ydl_opts = {"format": "bestaudio", "outtmpl": filename}

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        source = discord.FFmpegOpusAudio(
            filename,
            options=f"-filter_complex [0:a:0]volume=0.15,asetrate={rate}*48k,aresample=resampler=soxr:precision=24:osf=s32:tsf=s32p:osr=48k[out] -map [out]",
        )

        return source, filename
