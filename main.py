import json
from enum import Enum
import math
from itertools import groupby

# Pulsus Handing Helper
#
# Goal: Create an easy to use algorithm that detects the ideal handing  methods in pulsus maps.
# Parameters such as strain or number of fingers used may be tweaked to change the handing outcome.
# The algorithm may easily be implemented into other useful mapping tools, like an auto colorer or a star rating algorithm
#
# Program Architecture: There are four main classes: Note, Chord, Map, and HandingParser
# Note contains fundamental note data such as the tile or color, and helper methods to manipulate the data.
# There are also some auxiliary properties that utilize enums, such as Hand, Row, and Column.
# Chord groups Notes that occur at the same time for ease-of-coding, including single notes as "single note chords".
# Map collects Chords into a list and has tools to read and write maps.
# HandingParser takes a map and returns a new map where the Hand properties in each Note are "corrected" by the handing algorithm.
#
# Algorithm description: This is extremely WIP! It is missing core optimizations and pattern recognition!
# Every note will be referred to as chords, including single notes.
# Thats because it is how it is (will be) coded, even if it is not played like that.
# The algorithm has two main "tools" (idk what to call these): The "iterative feedforward" tool and the "default handing" tool .
# The iterative feedforward tool is the core part of the algorithm.
# A chord will use the previous notes handing to inform its handing (the previous note "feeds" its handing data "forward")
# This decision will be made based on a few parameters which will be detailed in another section.
# Many of these parameters are "thresholds" e.g. too much strain on one hand.
# If that threshold is maxed it will "reverse" the algorithm and start a new iteration with the "problem" handing changed.
# It will continuously repeat this until valid handing is found. (should probably repeat this until the optimal handing is found, but well see how fucked this is lol)
# I believe this is similar to A* somewhat? But I also think this is pretty innefficient lol.
# The default handing tool decides the handing of a chord in isolation.
# For example, the first chord in a map has no previous chord to base its handing off of, so it will use this.
# Once there is a long enough rest between chords, it will reset handing and use this rather than the iterative feedforward
#
# Iterative feedforward:
# As described before, a note will detect its handing using the handing of the note immediately before it.
# The way it detects its' handing is by using a priority system based on distance and angle.
# It will detect "roll" "alt" or "overload" and will either stay the same hand or alternate the hand.
# If both are plausible, then the hand will be marked as either.
# If the previous note was above this note, rolling is more likely.
# If the previous note is below, alting is more likely
#


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

        self.hand = Hand.RIGHT

    def set_hue(self, hue: int) -> None:
        self._hue = max(min(hue, 255), 0)

    def set_sat(self, sat: int) -> None:
        self._sat = max(min(sat, 255), 0)

    def set_bri(self, bri: int) -> None:
        self._bri = max(min(bri, 255), 0)

    def color_self(self) -> None:
        self.sat = 255
        self.bri = 255
        if self.hand == Hand.RIGHT:
            self.set_hue(141)
        elif self.hand == Hand.LEFT:
            self.set_hue(0)
        else:
            self.set_hue(70)

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


class Chord:
    def __init__(self, notes: list[Note]):
        self.notes: list[Note] = notes
        self.time: int = self.notes[0]._time
        self.count = len(self.notes)

    def color_self(self):
        for note in self.notes:
            note.color_self()


class Map:
    def __init__(self, chords=[]):
        self.chords: list[Chord] = chords

    def map_from_ttbeat_json(self, filepath="beats.json"):
        with open(filepath, "r") as f:
            mapdata = json.load(f)

        notes = []
        for note in mapdata:
            new_beat = Note(note[0], round(note[1]*500), note[5],
                            round(note[6]*500), note[11], note[16], note[17], note[9], note[10], note[13], note[14], note[1], note[6])
            notes.append(new_beat)
        chord_list = [list(note) for _, note in groupby(
            notes, key=lambda note: note._time)]
        self.chords = [Chord(chord) for chord in chord_list]
        return self

    def map_data_to_ttbeat_json(self, filepath="new_beats.json"):
        json_notes = []
        for chord in self.chords:
            for note in chord.notes:
                json_notes.append([
                    note._tile.value,
                    note._pulsus_time,
                    False,
                    0,
                    False,
                    note._type.value,
                    note._pulsus_hold_length,
                    0,
                    0,
                    note._bpm,
                    note._offset,
                    note._hue,
                    None,
                    note._transition_in,
                    note._transition_out,
                    True,
                    note._sat,
                    note._bri
                ])
        with open(filepath, "w") as f:
            json.dump(json_notes, f, indent=4)


class HandingParser:
    def __init__(self, map):
        self.map: Map = map
        self.default_threshold = 350  # around 1 beat at 180 bpm
        self.min_overload_time = 80  # 200 bpm 1/4 jack/overload time
        self.trill_strain_threshold = 1  # idk
        self.max_fingers_per_hand = 2
        self.parsed_map = self.parse_handing()

    def default_handing(self, chord: Chord):
        for note in chord.notes:
            if note.column == Column.LEFT:
                note.hand = Hand.LEFT
            elif note.column == Column.RIGHT:
                note.hand = Hand.RIGHT
            else:
                note.hand = Hand.EITHER

        for note in chord.notes:
            if note.hand == Hand.EITHER and any(n.hand == Hand.RIGHT for n in chord.notes):
                note.hand = Hand.RIGHT
            elif note.hand == Hand.EITHER and any(n.hand == Hand.LEFT for n in chord.notes):
                note.hand = Hand.LEFT
        chord.color_self()

    def parse_handing(self):
        split_maps: list[Map] = []
        previous_split_index = 0
        for i in range(len(self.map.chords)):
            if i == 0:
                continue

            if self.map.chords[i].time - self.map.chords[i-1].time >= self.default_threshold:
                split_maps.append(
                    Map(self.map.chords[previous_split_index:i-1]))
        split_maps.append(Map(self.map.chords[previous_split_index:]))

        parsed_chords: list[Chord] = []
        for map in split_maps:
            for chord in map.chords:
                self.default_handing(chord)
            parsed_chords.append(map.chords)
        parsed_map = Map(parsed_chords)
        return parsed_map


def main():
    map = Map().map_from_ttbeat_json()
    parser = HandingParser(map)
    Map.map_data_to_ttbeat_json(parser.parsed_map)


main()
