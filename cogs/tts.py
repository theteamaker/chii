import boto3
from botocore.config import Config

polly = boto3.client("polly")

def gen_speech(voiceid, text):   # Returns a StreamingBody whose contents should be thrown into an ogg.

    tts = polly.synthesize_speech(
        Engine="standard",
        OutputFormat="ogg_vorbis",
        Text=text,
        VoiceId=voiceid
    )

    return tts['AudioStream'].read()