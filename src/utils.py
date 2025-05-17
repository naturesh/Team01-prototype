import base64
import numpy as np
import torch


# TinyDB, wav array 저장 도구 


import base64
import io
import torchaudio

def base64_to_tensor(b64_str: str):
    audio_bytes = base64.b64decode(b64_str)
    with io.BytesIO(audio_bytes) as audio_file:
        waveform, sample_rate = torchaudio.load(audio_file)
    return waveform, sample_rate


