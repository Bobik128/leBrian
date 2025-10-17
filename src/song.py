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

speed: float = 2

_audio_lock = asyncio.Lock()

async def play(freq, note, dynamic = speed):
    duration = dynamic * note
    ms = int(round(duration * 1000))
    async with _audio_lock:
        audio.play_tone(int(round(freq)), ms)
    await asyncio.sleep(duration)

async def wait(note, dynamic = speed):
    await asyncio.sleep(dynamic * note)

# Duration helpers
W = 1.0     # whole
H = 1/2     # half
Q = 1/4     # quarter
E = 1/8     # eighth
S = 1/16    # sixteenth

async def REST(dur):  # visual phrasing helper
    await wait(dur)

async def main():
    # THEME A — line 1 (you started this; kept intact and continued)
    await play(E5, Q)
    await play(B4, E)
    await play(C5, E)
    await play(D5, E)
    await play(E5, S)
    await play(D5, S)
    await play(C5, E)
    await play(B4, E)
    await play(A4, Q)
    await play(A4, E)
    await play(C5, E)
    await play(E5, Q)
    await play(D5, E)
    await play(C5, E)
    await play(B4, Q)
    await REST(E)

    # THEME A — line 2
    await play(C5, E)
    await play(D5, E)
    await play(E5, Q)
    await play(C5, Q)
    await play(A4, Q)
    await play(A4, H)  # hold to finish the phrase
    await REST(E)

    # THEME A — line 3 (climb and fall)
    await play(D5, Q)
    await play(F5, E)
    await play(A5, Q)
    await play(G5, E)
    await play(F5, E)
    await play(E5, Q)
    await play(C5, E)
    await play(E5, E)
    await play(D5, Q)
    await play(C5, E)
    await play(B4, E)
    await play(B4, E)
    await play(C5, E)
    await play(D5, Q)
    await play(E5, Q)
    await play(C5, Q)
    await play(A4, Q)
    await play(A4, H)
    await REST(E)

    # THEME A — line 4 (repeat of line 1 tail)
    await play(E5, Q)
    await play(B4, E)
    await play(C5, E)
    await play(D5, E)
    await play(E5, S)
    await play(D5, S)
    await play(C5, E)
    await play(B4, E)
    await play(A4, Q)
    await play(A4, E)
    await play(C5, E)
    await play(E5, Q)
    await play(D5, E)
    await play(C5, E)
    await play(B4, Q)
    await REST(E)

    # THEME A — line 5 (closing)
    await play(C5, E)
    await play(D5, E)
    await play(E5, Q)
    await play(C5, Q)
    await play(A4, Q)
    await play(A4, H)
    await REST(Q)

    # THEME B — line 1 (bright variant)
    await play(E5, Q)
    await play(C5, E)
    await play(D5, E)
    await play(B4, Q)
    await play(C5, E)
    await play(A4, E)
    await play(G4, Q)
    await play(A4, E)
    await play(C5, E)
    await play(E5, Q)
    await play(D5, E)
    await play(C5, E)
    await play(B4, Q)
    await REST(E)

    # THEME B — line 2
    await play(C5, E)
    await play(D5, E)
    await play(E5, Q)
    await play(C5, Q)
    await play(A4, Q)
    await play(A4, H)
    await REST(Q)

    # THEME B — line 3 (up to the top)
    await play(E5, Q)
    await play(C5, E)
    await play(D5, E)
    await play(B4, Q)
    await play(C5, E)
    await play(A4, E)
    await play(G4, Q)
    await play(A4, E)
    await play(C5, E)
    await play(D5, E)
    await play(E5, E)
    await play(F5, E)
    await play(E5, E)
    await play(D5, E)
    await play(C5, E)
    await play(B4, E)
    await play(A4, Q)
    await play(A4, H)
    await REST(Q)

    # THEME A — reprise (short)
    await play(E5, Q)
    await play(B4, E)
    await play(C5, E)
    await play(D5, E)
    await play(E5, S)
    await play(D5, S)
    await play(C5, E)
    await play(B4, E)
    await play(A4, Q)
    await play(A4, E)
    await play(C5, E)
    await play(E5, Q)
    await play(D5, E)
    await play(C5, E)
    await play(B4, H)

# run
asyncio.run(main())