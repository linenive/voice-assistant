import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from .config import SAMPLE_RATE, CHANNELS, RECORDING_PATH, INPUT_DEVICE

def record(duration=10):
    """버튼 누르는 동안 녹음"""
    print("녹음 중...")
    frames = []
    
    while is_pressed_func():
        chunk = sd.rec(
            int(0.1 * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='int16',
            device=INPUT_DEVICE
        )
        sd.wait()
        frames.append(chunk)
    
    if frames:
        audio = np.concatenate(frames, axis=0)
        wav.write(RECORDING_PATH, SAMPLE_RATE, audio)
        print("녹음 완료!")
        return True

def record_while_pressed(is_pressed_func):
    """버튼 누르는 동안만 녹음"""
    print("녹음 중...")
    frames = []
    
    while is_pressed_func():
        chunk = sd.rec(
            int(0.1 * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='int16',
            device=INPUT_DEVICE
        )
        sd.wait()
        frames.append(chunk)
    
    if frames:
        audio = np.concatenate(frames, axis=0)
        wav.write(RECORDING_PATH, SAMPLE_RATE, audio)
        print("녹음 완료!")
        return True
    return False