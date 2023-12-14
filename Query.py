class Query:
    def __init__(self, genre, track, is_artist=False):
        self.genre = int(genre)
        self.track = int(track)
        self.is_artist = int(is_artist)

    def as_list(self):
        return [self.genre, self.track, self.is_artist]
