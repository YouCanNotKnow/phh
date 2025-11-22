from note import Note, FingerNote
import copy


class Chord:
    def __init__(self, notes: list[Note]):
        if len(notes) == 0:
            raise Exception("Chord notes length = 0")
        if any(note.time != notes[0].time for note in notes):
            raise Exception("Chord notes not a chord")

        self.notes: list[Note] = notes
        self.time: int = self.notes[0].time
        self.count = len(self.notes)


class FingerChord:
    def __init__(self, fnotes: list[FingerNote]):
        if len(fnotes) == 0:
            raise Exception("FingerChord notes length = 0")
        if any(fnote.note.time != fnotes[0].note.time for fnote in fnotes):
            raise Exception("FingerChord notes not a chord")

        self._fnotes: list[FingerNote] = fnotes

    @property
    def fnotes(self) -> list[FingerNote]:
        return copy.deepcopy(self._fnotes)

    @property
    def time(self) -> int:
        return self.fnotes[0].note.time

    @property
    def count(self) -> int:
        return len(self.fnotes)

    def color_self(self) -> None:
        for fnote in self.fnotes:
            fnote.color_self()
