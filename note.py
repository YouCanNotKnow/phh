from common import Column, Hand, NoteType, Row, Tile, Finger
import math


class Note:
    def __init__(self,
                 tile: int,
                 time: int,
                 type: int,
                 hold_length: int,
                 hue: int,
                 sat: int,
                 bri: int,
                 bpm: int,
                 offset: int,
                 transition_in: int,
                 transition_out: int,
                 pulsus_time: float,
                 pulsus_hold_length: float):
        self._tile: Tile = Tile(tile)
        self._time: int = time
        self._type: NoteType = NoteType(type)
        self._hold_length: int = hold_length
        self._hue: int = hue
        self._sat: int = sat
        self._bri: int = bri
        self._pulsus_time = pulsus_time
        self._pulsus_hold_length = pulsus_hold_length

        self._bpm = bpm
        self._offset = offset
        self._transition_in = transition_in
        self._transition_out = transition_out

    def set_hue(self, hue: int) -> None:
        self._hue = max(min(hue, 255), 0)

    def set_sat(self, sat: int) -> None:
        self._sat = max(min(sat, 255), 0)

    def set_bri(self, bri: int) -> None:
        self._bri = max(min(bri, 255), 0)

    @property
    def tile(self) -> Tile:
        return self._tile

    @property
    def time(self) -> int:
        return self._time

    @property
    def column(self) -> Column:
        return Column(self._tile.value % 3)

    @property
    def row(self) -> Row:
        return Row(math.floor(self._tile.value / 3))


class FingerNote:
    def __init__(self, note: Note, finger: Finger):
        self.note: Note = note
        self.finger: Finger = finger

    @property
    def hand(self):
        return self.finger.hand

    def color_self(self) -> None:
        self.note.set_sat(255)
        self.note.set_bri(255)
        if self.finger.hand == Hand.RIGHT:
            self.note.set_hue(141)
        elif self.finger.hand == Hand.LEFT:
            self.note.set_hue(0)
        else:
            self.note.set_hue(70)
