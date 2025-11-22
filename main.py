from common import Column, Hand, NoteType, Row, Tile, Finger
from note import Note, FingerNote
from chord import Chord, FingerChord
from map import Map, FingerMap

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
    def __init__(self, finger: Finger, tile: Tile, time_held: int):
        self._finger = finger
        self._tile = tile
        self.time_held = time_held


class HandingIterator:
    def __init__(self, map):

        pass


class HandingParser:
    def __init__(self, map: Map) -> None:
        self.map: Map = map
        self.default_threshold = 350  # around 1 beat at 180 bpm
        self.min_overload_time = 80  # 200 bpm 1/4 jack/overload time
        self.release_time = 50
        self.max_fingers_per_hand = 2
        self.parsed_map = self.parse_handing()

    def default_handing(self, chord: Chord) -> FingerChord:
        fnotes: list[FingerNote] = []
        for note in chord.notes:
            if note.column == Column.LEFT:
                fnotes.append(FingerNote(note, Finger.LA))
            elif note.column == Column.RIGHT:
                fnotes.append(FingerNote(note, Finger.RA))
            else:
                fnotes.append(FingerNote(note, Finger.EA))
        for fnote in fnotes:
            if fnote.hand == Hand.EITHER and any(n.hand == Hand.RIGHT for n in fnotes):
                finger = Finger.RA
            elif fnote.hand == Hand.EITHER and any(n.hand == Hand.LEFT for n in fnotes):
                finger = Finger.LA

        fchord: FingerChord = FingerChord(fnotes)
        fchord.color_self()
        return fchord

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
            for chord in map.chords:
                parsed_chords.append(self.default_handing(chord))
        parsed_map = FingerMap(parsed_chords)
        return parsed_map

# class has list of chords (map)
# has a cursor
# has next method that increments and decrements the cursor
# has a get method that gets value at cursor

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


def main():
    map = Map().map_from_ttbeat_json()
    parser = HandingParser(map)
    FingerMap.map_data_to_ttbeat_json(parser.parsed_map)


if __name__ == "__main__":
    main()
