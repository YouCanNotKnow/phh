import json
from chord import Chord, FingerChord
from note import Note, FingerNote
from itertools import groupby


class Map:
    def __init__(self, chords: list[Chord] = []) -> None:
        self.chords: list[Chord] = chords

    def map_from_ttbeat_json(self, filepath="beats.json") -> "Map":
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


class FingerMap:
    def __init__(self, fchords: list[FingerChord] = []) -> None:
        self.fchords: list[FingerChord] = fchords

    def map_data_to_ttbeat_json(self, filepath="new_beats.json"):
        json_notes = []
        for fchord in self.fchords:
            for fnote in fchord.fnotes:
                note = fnote.note
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
