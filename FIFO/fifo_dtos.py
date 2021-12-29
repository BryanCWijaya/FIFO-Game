class LevelDetailsDto:
    def __init__(self, level_id,  level, normal_book, big_book, max_book_strength, min_score):
        self.level = level
        self.num_of_book = normal_book
        self.num_of_big_book = big_book
        self.max_book_strength = max_book_strength
        self.min_score = min_score
        self.level_id = level_id


class LevelDataDto:
    def __init__(self, level_id, level, book_stack, min_score):
        self.level = level
        self.book_stack = book_stack
        self.min_score = min_score
        self.level_id = level_id


class UserDto:
    def __init__(self, username= None, email= None, password= None, level= None):
        self.username = username
        self.password = password
        self.email = email
        self.level = level

class ScoreDto:
    def __init__(self, scores: list):
        self.scores = scores


class ErrorDto:
    def __init__(self, msg: int):
        self.msg = msg

class FriendAndRequestDto:
    def __init__(self, friends: list, friend_request: list):
        self.friends = friends  # username, last online
        self.friend_request = friend_request

class CheckRequestDto:
    def __init__(self, is_exist, already_req):
        self.is_exist = is_exist
        self.already_requested = already_req

class EmailDto:
    def __init__(self, email):
        self.email = email

class AverageQuery:
    def __init__(self, min_score, average_score):
        self.min_score = min_score
        self.average_score = average_score
