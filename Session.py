import numpy as np
import SongLibrary
from Query import Query


class Session:
    def __init__(self, player, era, artist_answers, title_answers, ratings, is_new=False):
        self.player = player
        self.era = era
        genre_count = 9 if era == 1 else 12
        self.artist_score = np.zeros([genre_count, 13], dtype=int)
        self.title_score = np.zeros([genre_count, 13], dtype=int)
        self.rating = np.array(ratings).reshape(genre_count, 13)
        self.artist_answers = artist_answers
        self.title_answers = title_answers
        self.queries = []
        if is_new:
            self.fast_evaluate()

    def as_row(self):
        queries_list = []
        for query in self.queries:
            queries_list += query.as_list()
        return [self.player, self.era] + [i for i in self.artist_score.reshape(-1).tolist()] + \
               [i for i in self.title_score.reshape(-1).tolist()] + \
               [i for i in self.rating.reshape(-1).tolist()] + self.artist_answers + self.title_answers + queries_list

    def summary(self):
        result = []
        genre_count, track_count = self.artist_score.shape
        for genre_number in range(genre_count):
            genre_name = SongLibrary.get_genre(self.get_genre(genre_number))
            for track_number in range(track_count):
                artist_prompt = SongLibrary.get_prompt(self.get_genre(genre_number), track_number, True)
                artist_answer = self.get_answer(genre_number, track_number, True)
                artist_score = self.artist_score[genre_number, track_number]
                title_prompt = SongLibrary.get_prompt(self.get_genre(genre_number), track_number)
                title_answer = self.get_answer(genre_number, track_number)
                title_score = self.title_score[genre_number, track_number]
                result.append([genre_name, artist_prompt, artist_answer, artist_score, title_prompt, title_answer,
                               title_score])
        return result

    def get_genre(self, genre):
        if self.era == 2:
            offset = 9
        elif self.era == 3:
            offset = 21
        else:
            offset = 0
        return offset + genre

    def fast_evaluate(self):
        genre_count, track_count = self.artist_score.shape
        for genre_number in range(genre_count):
            for track_number in range(track_count):
                artist_answer = self.get_answer(genre_number, track_number, True)
                title_answer = self.get_answer(genre_number, track_number)
                if len(artist_answer) <= 2:
                    pass
                elif SongLibrary.match_answer(artist_answer, self.get_genre(genre_number), track_number, True) >= 0.9:
                    self.artist_score[genre_number, track_number] = 2
                else:
                    self.queries.append(Query(genre_number, track_number, True))
                if len(title_answer) <= 2:
                    pass
                elif SongLibrary.match_answer(title_answer, self.get_genre(genre_number), track_number) >= 0.9:
                    self.title_score[genre_number, track_number] = 2
                else:
                    self.queries.append(Query(genre_number, track_number))

    def add_query(self, genre, track, is_artist):
        self.queries.append(Query(genre, track, is_artist == 1))

    def get_answer(self, genre, track, is_artist=False):
        if is_artist:
            return self.artist_answers[int(genre * 13 + track)]
        else:
            return self.title_answers[int(genre * 13 + track)]

    def judge_first_query(self, score):
        if self.queries[0].is_artist:
            self.artist_score[int(self.queries[0].genre), int(self.queries[0].track)] = score
        else:
            self.title_score[int(self.queries[0].genre), int(self.queries[0].track)] = score
        del self.queries[0]
