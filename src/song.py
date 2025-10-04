import brian.audio as audio
import time

C4 = 261.63
C4_plus = 277.18
D4_minus = C4_plus
D4 = 293.66
D4_plus = 311.13
E4_minus = D4_plus
E4 = 329.63
F4 = 349.23
F4_plus = 369.99
G4_minus = F4_plus
G4 = 392.00
G4_plus = 415.30
A4_minus = G4_plus
A4 = 440.00
A4_plus = 466.16
B4_minus = A4_plus
B4 = 493.88

C5 = 523.25
C5_plus = 554.37
D5_minus = C5_plus
D5 = 587.33
D5_plus = 622.25
E5_minus = D5_plus
E5 = 659.26
F5 = 698.46
F5_plus = 739.99
G5_minus = F5_plus
G5 = 783.99
G5_plus = 830.61
A5_minus = G5_plus
A5 = 880.00
A5_plus = 932.33
B5_minus = A5_plus
B5 = 987.77


def play(freq, duration):
    """
    :param freq: note freq Hz
    :param duration: duration in s
    :return:
    """

    audio.play_tone(round(freq), round(duration * 1000))  # hz, ms
    time.sleep(duration)


bpm = 45
f = 60 / bpm / 1
h = 60 / bpm / 2
q = 60 / bpm / 4
s = 60 / bpm / 8

time.sleep(1)


def bbcd():
    play(B4, q)
    play(B4, q)
    play(C5, q)
    play(D5, q)


def dcba():
    play(D5, q)
    play(C5, q)
    play(B4, q)
    play(A4, q)


def ggab():
    play(G4, q)
    play(G4, q)
    play(A4, q)
    play(B4, q)


def baa():
    play(B4, q + s)
    play(A4, s)
    play(A4, h)


def agg():
    play(A4, q + s)
    play(G4, s)
    play(G4, h)


def aabg():
    play(A4, q)
    play(A4, q)
    play(B4, q)
    play(G4, q)


def abcbg():
    play(A4, q)
    play(B4, s)
    play(C5, s)
    play(B4, q)
    play(G4, q)


def abcba():
    play(A4, q)
    play(B4, s)
    play(C5, s)
    play(B4, q)
    play(A4, q)


def gad():
    play(G4, q)
    play(A4, q)
    play(D4, h)


# --- start ---

bbcd()
dcba()
ggab()
baa()
bbcd()
dcba()
ggab()
agg()
aabg()
abcbg()
abcba()
gad()
bbcd()
dcba()
ggab()
agg()