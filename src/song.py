import brian.audio as audio
import asyncio
import time

C4 = 261.63; C4_plus = 277.18; D4_minus = C4_plus
D4 = 293.66; D4_plus = 311.13; E4_minus = D4_plus
E4 = 329.63; F4 = 349.23; F4_plus = 369.99; G4_minus = F4_plus
G4 = 392.00; G4_plus = 415.30; A4_minus = G4_plus
A4 = 440.00; A4_plus = 466.16; B4_minus = A4_plus; B4 = 493.88

C5 = 523.25; C5_plus = 554.37; D5_minus = C5_plus
D5 = 587.33; D5_plus = 622.25; E5_minus = D5_plus
E5 = 659.26; F5 = 698.46; F5_plus = 739.99; G5_minus = F5_plus
G5 = 783.99; G5_plus = 830.61; A5_minus = G5_plus
A5 = 880.00; A5_plus = 932.33; B5_minus = A5_plus; B5 = 987.77

# tempo
bpm = 45
f = 60 / bpm / 1   # whole note (semibreve)
h = 60 / bpm / 2   # half
q = 60 / bpm / 4   # quarter
s = 60 / bpm / 8   # eighth

speed: float = 2

# Global lock so tones don't interrupt each other on a single speaker.
_audio_lock = asyncio.Lock()

async def play(freq, note, dynamic = speed):
    """freq in Hz, duration in seconds."""
    duration = dynamic * note
    ms = int(round(duration * 1000))
    async with _audio_lock:
        audio.play_tone(int(round(freq)), ms)  # non-blocking: starts tone
    # Sleep for the *actual* duration in seconds (no /1000!)
    await asyncio.sleep(duration)

async def wait(note, dynamic = speed):
    await asyncio.sleep(dynamic * note)

async def main():
    # await play(G4, speed, 1/4)
    # await wait(speed, 1/4)
    await play(E5, 1/4)
    await play(B4, 1/8)
    await play(C5, 1/8)
    await play(D5, 1/8)
    await play(E5, 1/16)
    await play(D5, 1/16)
    await play(C5, 1/8)
    await play(B4, 1/8)

asyncio.run(main())
