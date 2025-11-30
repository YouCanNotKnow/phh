from common import Column, Hand, NoteType, Row, Tile, Finger
from note import Note, FingerNote
from chord import Chord, FingerChord
from map import Map, FingerMap
from typing import TypeAlias

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


class PressedFinger:
    def __init__(self, finger: Finger, press_time: int, type: int, hold_length: int):
        self._finger: Finger = finger
        self._press_time: int = press_time
        self._type: int = type
        self._hold_length: int = hold_length
        self.time_held: int = 0

    @property
    def finger(self) -> Finger:
        return self._finger

    @property
    def press_time(self) -> int:
        return self._press_time

    @property
    def type(self) -> int:
        return self._type

    @property
    def hold_length(self) -> int:
        return self._hold_length


class HandingIterator:
    def __init__(self, fmap: FingerMap):
        self.cursor: int = 0
        self.fmap: FingerMap = fmap
        PFingersTuple: TypeAlias = tuple[None | PressedFinger, None | PressedFinger, None | PressedFinger,
                                         None | PressedFinger, None | PressedFinger, None | PressedFinger,
                                         None | PressedFinger, None | PressedFinger, None | PressedFinger]
        self.pressed_fingers: PFingersTuple = (None, None, None,
                                               None, None, None,
                                               None, None, None)
        self.previous_fingers: list[PFingersTuple] = []

    def next_chord(self):
        if self.cursor + 1 > len(self.fmap.fchords):
            raise Exception("Cursor greater than map length")

        self.reset_fingers(self.read_cursor())
        # currently Ignorantly overwrites pressed fingers.
        new_pfingers = list(self.pressed_fingers)
        for fnote in self.read_cursor().fnotes:
            new_pfingers[fnote.note.tile.value] = PressedFinger(
                fnote.finger, fnote.time, fnote.note.type, fnote.note.hold_length)
        self.pressed_fingers = tuple(new_pfingers)
        self.cursor += 1

    def prev_chord(self):
        if cursor - 1 < 0:
            raise Exception("Cursor less than 0")
        cursor -= 1

    def read_cursor(self) -> FingerChord:
        return self.fmap.fchords[self.cursor]

    def reset_fingers(self, next_fchord: FingerChord):
        self.previous_fingers.append(self.pressed_fingers)
        new_pfingers = list(self.pressed_fingers)
        for pfinger in new_pfingers:
            if pfinger is None:
                continue

            if pfinger.type is NoteType.BEAT:
                pfinger = None
                continue

            pfinger.time_held += next_fchord.time - pfinger.press_time
            if pfinger.time_held >= pfinger.hold_length:
                pfinger = None
                continue
        self.pressed_fingers = tuple(new_pfingers)


class HandingParser:
    def __init__(self, map: Map) -> None:
        self.map: Map = map
        self.default_threshold: float = 350  # around 1 beat at 180 bpm
        self.min_overload_time: float = 80  # 200 bpm 1/4 jack/overload time
        self.release_time: float = 50
        self.max_fingers_per_hand: int = 2
        self.parsed_map: FingerMap = self.parse_handing()

        # NOTE THESE ARE WRITTEN AS TILES ON THE NUMPAD FOR EASE OF EDITING
        # the basis of this map is based on distance and angles. prefer short distances with inward angles
        # then downwards diagonal to downwards angles
        # then gradual upwards angles
        # there are some symmetries on the pulsus board like if i was hitting 5 into 4 or 6 thats technically the same.
        # because these lists are ordered, the lists prefer *going right* to emulate right hand dominance
        # on vertical symmetries lik 963, prefer downwards
        # shouldnt change much idk
        self._tile_handing_map: dict[int, list[int]] = {
            7: [8, 5, 4, 2, 1, 9, 6, 3],
            8: [9, 6, 5, 3, 2, 7, 4, 1],
            9: [8, 5, 6, 2, 3, 7, 4, 1],
            4: [5, 2, 1, 8, 7, 6, 3, 9],
            5: [6, 4, 9, 7, 8, 3, 1, 2],
            6: [5, 2, 3, 8, 9, 4, 1, 7],
            1: [2, 5, 4, 8, 7, 3, 6, 9],
            2: [3, 1, 6, 4, 9, 7, 5, 8],
            3: [2, 5, 6, 8, 9, 1, 4, 7]
        }
        tile_mapping: dict[int, int] = {
            7: 0, 8: 1, 9: 2, 4: 3, 5: 4, 6: 5, 1: 6, 2: 7, 3: 8}
        self.tile_handing_map: dict[int, list[int]] = {
            tile_mapping[k]: [tile_mapping[x] for x in v]
            for k, v in self._tile_handing_map.items()
        }

    def default_handing(self, chord: Chord) -> FingerChord:
        fnotes: list[FingerNote] = []
        for note in chord.notes:
            if note.column == Column.LEFT:
                fnotes.append(FingerNote(note, Finger.LM))
            elif note.column == Column.RIGHT:
                fnotes.append(FingerNote(note, Finger.RM))
            else:
                fnotes.append(FingerNote(note, Finger.EI))

        fchord: FingerChord = FingerChord(fnotes)
        fchord.color_self()
        return fchord

    def iterate_handing(self, fmap: FingerMap) -> FingerMap:
        iterator: HandingIterator = HandingIterator(fmap)
        iterated_fchords = []
        for i in range(len(fmap.fchords)):
            iterated_fchords.append(iterator.read_cursor())
            iterator.next_chord()
        return FingerMap(iterated_fchords)

    def parse_handing(self) -> FingerMap:
        split_maps: list[Map] = []
        previous_split_index = 0
        for i in range(len(self.map.chords)):
            if i == 0:
                continue

            if self.map.chords[i].time - self.map.chords[i-1].time >= self.default_threshold:
                split_maps.append(
                    Map(self.map.chords[previous_split_index:i-1]))
                previous_split_index = i

        split_maps.append(Map(self.map.chords[previous_split_index:]))
        parsed_chords: list[FingerChord] = []
        for map in split_maps:
            split_parsed_chords: list[FingerChord] = []
            for chord in map.chords:
                split_parsed_chords.append(self.default_handing(chord))
            split_parsed_map = FingerMap(split_parsed_chords)
            iterated_parsed_map: FingerMap = self.iterate_handing(
                split_parsed_map)
            for fchord in iterated_parsed_map.fchords:
                parsed_chords.append(fchord)
        parsed_map: FingerMap = FingerMap(parsed_chords)
        return parsed_map

# create engine that takes a map and associated handing and calculates a score for the handing
# then create a search algorithm to optimize that handing

# tuple
# for each tile, if nothing else is pressed, heres the priority for what finger should be used next
# when going to press a key, you have in memory the other keys pressed, so when pressing the new key go through the priority list and use it if possible
# dictionary!

# do the backward stuff later, just do an initial sweep for now
# use dfs/bfs idk

# [note with known handing, all the other notes]
# cursor
# (None x9)
# (None, None, (class/dictionary containing press time and finger), None x6)
# for jacks, store the previous finger on the tile and just rehit that. if the next note is too fast on some threshold,
# instead alternate on the other hand
# might need to specify finger maps for each specific finger??? idk


def main():
    map = Map().map_from_ttbeat_json()
    parser = HandingParser(map)
    FingerMap.map_data_to_ttbeat_json(parser.parsed_map)


if __name__ == "__main__":
    main()
