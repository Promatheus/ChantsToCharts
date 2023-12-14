import SongLibrary
from Session import Session

genders = ["Férfi", "Nő"]
ratings = ["Már fáj!", "Ugorgyunk", "Nyeh", "Maradhat", "Vájbolom!"]
sessions = []


def count_queries():
    result = 0
    for session in sessions:
        if session.queries:
            result += len(session.queries)
    return result


def prompt_query():
    for session in sessions:
        if session.queries:
            query = session.queries[0]
            prompt = SongLibrary.get_prompt(session.get_genre(query.genre), query.track, query.is_artist)
            answer = session.get_answer(query.genre, query.track, query.is_artist)
            return [prompt, answer]
    return []


def judge_query(score):
    for session in sessions:
        if session.queries:
            session.judge_first_query(score)
            break


def session_exists(player, era):
    return any(x for x in sessions if x.player == player and x.era == era)


def common_eras(chosen_players):
    eras = [1, 2, 3]
    result = []
    for era in eras:
        if all([session_exists(chosen_player, era) for chosen_player in chosen_players]):
            result.append(era)
    return result


def genres_per_eras(chosen_eras):
    result = []
    for era in chosen_eras:
        if era == 1:
            result.append(SongLibrary.genres[0:9])
        elif era == 2:
            result.append(SongLibrary.genres[9:21])
        elif era == 3:
            result.append(SongLibrary.genres[21:33])
        else:
            pass
    return result


def summary(player, eras):
    result = []
    for era in eras:
        result += get_session(player, era).summary()
    return list(map(list, zip(*result)))


def get_session(player, era):
    for choosable_session in sessions:
        if choosable_session.player == player and choosable_session.era == era:
            return choosable_session
        else:
            pass
    return None


def player_exists(player):
    return any(x for x in sessions if x.player == player)


def players():
    return set(str(session.player) for session in sessions)


def delete_players(player):
    for i, session in enumerate(sessions):
        if session.player == player:
            del sessions[i]


def get_era(row_length):
    if row_length == 347:
        return 1
    elif row_length == 470:
        return 2
    elif row_length == 473:
        return 3
    else:
        return 0


def get_rating(raw_string):
    if raw_string in ratings:
        return int(ratings.index(raw_string) + 1)
    else:
        return 0


def load_session(raw_data):
    offset = 2
    tracks_count = 117 if int(raw_data[1]) == 1 else 156
    rating_answers = raw_data[offset + tracks_count * 2:offset + tracks_count * 3]
    artist_answers = raw_data[offset + tracks_count * 3:offset + tracks_count * 4]
    title_answers = raw_data[offset + tracks_count * 4:offset + tracks_count * 5]
    result = Session(raw_data[0], int(raw_data[1]), artist_answers, title_answers, rating_answers)
    result.artist_score.flat = raw_data[offset:offset + tracks_count]
    result.title_score.flat = raw_data[offset + tracks_count:offset + tracks_count * 2]

    query_count = int((len(raw_data) - offset - tracks_count * 5) / 3)
    for i in range(query_count):
        start_point = offset + tracks_count * 5 + i * 3
        result.add_query(raw_data[start_point], raw_data[start_point + 1], int(raw_data[start_point + 2]))
    sessions.append(result)


def create_session(raw_data):
    era = get_era(len(raw_data))
    if not session_exists(raw_data[1], era) and era != 0:
        artist_answers = []
        title_answers = []
        rating_answers = []
        if era == 1:
            title_answers += raw_data[4:12]
            artist_answers += ['']*8
            title_answers += raw_data[12:21:2]
            artist_answers += raw_data[13:22:2]
            rating_answers += (get_rating(i) for i in raw_data[22:35])
            for i in range(8):
                offset = 35 + i * 39
                title_answers += raw_data[offset:offset + 25:2]
                artist_answers += raw_data[offset + 1:offset + 26:2]
                rating_answers += (get_rating(i) for i in raw_data[offset + 26:offset + 39])
        else:
            for i in range(12):
                offset = 2 + i * 39
                title_answers += raw_data[offset:offset + 25:2]
                artist_answers += raw_data[offset + 1:offset + 26:2]
                rating_answers += (get_rating(i) for i in raw_data[offset + 26:offset + 39])
        sessions.append(Session(raw_data[1], era, artist_answers, title_answers, rating_answers, True))
