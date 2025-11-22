from enum import Enum


class Hand(Enum):
    RIGHT = 0
    LEFT = 1
    EITHER = 2


class Row(Enum):
    TOP = 0
    MIDDLE = 1
    BOTTOM = 2


class Column(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class NoteType(Enum):
    BEAT = 0
    HOLD = 1


class Tile(Enum):
    TL = 0
    TC = 1
    TR = 2
    ML = 3
    MC = 4
    MR = 5
    BL = 6
    BC = 7
    BR = 8


class Finger(Enum):
    RT = 1
    RI = 2
    RM = 3
    RR = 4
    RP = 5
    RA = 6
    LT = -1
    LI = -2
    LM = -3
    LR = -4
    LP = -5
    LA = -6
    ET = 11
    EI = 12
    EM = 13
    ER = 14
    EP = 15
    EA = 16

    @property
    def hand(self) -> Hand:
        match self:
            case Finger.RT | Finger.RI | Finger.RM | Finger.RR | Finger.RP | Finger.RA:
                return Hand.RIGHT
            case Finger.LT | Finger.LI | Finger.LM | Finger.LR | Finger.LP | Finger.LA:
                return Hand.LEFT
            case Finger.ET | Finger.EI | Finger.EM | Finger.ER | Finger.EP | Finger.EA:
                return Hand.EITHER
