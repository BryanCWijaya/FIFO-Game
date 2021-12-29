import numpy as np
from FIFO.displayable import Book, BigBook, BookStack
import random
from FIFO.fifo_repository import *
from datetime import datetime
from abc import abstractmethod


class Message:
    @abstractmethod
    def __init__(self, level, book_obtained, wrong_press, score):
        self.level = level
        self.book_obtained = book_obtained
        self.wrong_press = wrong_press
        self.score = score


class Observer:
    @abstractmethod
    def update(self, _message: Message):
        pass


class Subject:
    @abstractmethod
    def attach(self, _observer: Observer):
        pass

    @abstractmethod
    def detach(self, _observer: Observer):
        pass

    @abstractmethod
    def notify_update(self, _msg: Message):
        pass


class LevelSubject(Subject):
    def __init__(self):
        self.__observers = [] # menggunakan list agar bisa urut eksekusinya

    def attach(self, _observer: Observer):
        self.__observers.append(_observer)

    def detach(self, _observer: Observer):
        self.__observers.remove(_observer)

    def notify_update(self, _msg: Message):
        for o in self.__observers:
            o.update(_msg)


class LevelSuccess(Message):
    def __init__(self, level, book_obtained, wrong_press, score):
        self.level = level
        self.book_obtained = book_obtained
        self.wrong_press = wrong_press
        self.score = score


class LevelFailed(Message):
    def __init__(self, level, book_obtained, wrong_press, score):
        self.level = level
        self.book_obtained = book_obtained
        self.wrong_press = wrong_press
        self.score = score


class ThreeTimesLevelFailed(Observer):
    def __init__(self, username):
        self.username = username
        self.fail_streak = 0

    def send_email(self):
        print("You have lost for 3 times, try harder to succeed")

    def update(self, _message: Message):
        if isinstance(_message, LevelFailed):
            self.fail_streak += 1
            if self.fail_streak == 3:
                self.send_email()
        elif isinstance(_message, LevelSuccess):
            self.fail_streak = 0


class UnlockNewLevel(Observer):
    def __init__(self, level, username, repository):
        self.level = level
        self.username = username
        self.repository = repository

    def unlock_new_level(self, username):
        self.repository.increment_level(username)

    def update(self, _message: Message):
        if isinstance(_message, LevelSuccess):
            level_completed = _message.level
            if self.level == level_completed:  # unlock new level
                if self.level != 10:  # 10 is highest level
                    self.level += 1
                    self.unlock_new_level(self.username)


class SaveScore(Observer):
    def __init__(self, username, repository):
        self.username = username
        self.repository = repository

    def save_score(self, level, book_obtained, wrong_press, score, username):
        self.repository.save_score(level, book_obtained, wrong_press, score, username)

    def update(self, _message: Message):
        level = _message.level
        book_obtained = _message.book_obtained
        wrong_press = _message.wrong_press
        score = _message.score
        if level != 0:
            self.save_score(level, book_obtained, wrong_press, score, self.username)


class SuccessEnterLeaderboard(Observer):
    def __init__(self, username, repository):
        self.username = username
        self.repository = repository

    def get_top_score(self, level):
        score = self.repository.get_top_7_score(level)
        if len(score.scores) == 0:
            top_score = None
        else:
            top_score = score.scores
        return top_score

    def message_to_loser(self, username):
        loser_data = self.repository.get_user_data(username)
        if not isinstance(loser_data, ErrorDto):
            print(f"Email sent to {loser_data.email}: Your best score was beaten by someone ")

    def update(self, _message: Message):
        score = _message.score
        level = _message.level
        if level != 0:
            top_score = self.get_top_score(level)
            if top_score is None:
                print("You made it to the leaderboard")
            else:
                print("You made it to the leaderboard")
                for i in range(len(top_score)-1, -1, -1):
                    if score > top_score[i][1]:
                        loser_username = top_score[i][0]
                        if loser_username != self.username: # not myself
                            self.message_to_loser(loser_username)
                    else:
                        break

@inject
class FifoService:
    def __init__(self, repository1: UserScoreRepository, repository2: LevelRepository):
        self.user_and_score_repository = repository1
        self.level_repository = repository2

    def setup(self, username, email, level):
        self.subject = LevelSubject()
        self.subject.attach(ThreeTimesLevelFailed(username))
        self.subject.attach(UnlockNewLevel(level, username, self.user_and_score_repository))
        self.subject.attach(SuccessEnterLeaderboard(username, self.user_and_score_repository))
        self.subject.attach(SaveScore(username, self.user_and_score_repository))


    def single_player_setup(self, book_list, arrow_list, level, BigBookClass, BookStackClass):
        random.shuffle(book_list)
        level_details = self.level_repository.get_level_details(level)
        random_books = list(np.random.randint(low=0, high=4, size=level_details.num_of_book))
        books = [Book(book_list[code], arrow_list[code], code) for code in random_books]
        big_books_random_index = random.sample(range(level_details.num_of_book), level_details.num_of_big_book)
        for index in big_books_random_index:
            code = random_books[index]
            strength = random.randint(2, level_details.max_book_strength)
            books[index] = BigBookClass(book_list[code], arrow_list[code], code, strength)
        book_stack = BookStackClass(0, books)
        level_data = LevelDataDto(level_details.level_id, level_details.level, book_stack, level_details.min_score)
        return level_data

    def level_finish(self, level, book_obtained, wrong_press, score, code):  # 0 -> fail, 1 -> success
        if code == 1:
            msg = LevelSuccess(level, book_obtained, wrong_press, score)
        else:
            msg = LevelFailed(level, book_obtained, wrong_press, score)
        self.subject.notify_update(msg)

    def stack_pop(self, book_stack, key):
        if key == book_stack.books[0].code:
            if isinstance(book_stack.books[0], BigBook):
                if book_stack.books[0].is_one_strength_left():
                    popped = book_stack.update(pop=True)
                    return popped
                else:
                    book_stack.books[0].hit()
                    book_stack.update(pop=False)
                    return 0
            else:
                popped = book_stack.update(pop=True)
                return popped
        return -1

    def countdown(self, timer, count_from, always_return=False):
        if always_return:
            time_left = timer.get_time_left()
            if time_left <= count_from:
                return time_left
        else:
            time_left = timer.get_second_left()
            if time_left is not None:
                if time_left <= count_from:
                    return time_left

    def register_user(self, username, email, password):
        return self.user_and_score_repository.add_new_user(username, email, password)

    def verify_user(self, username, password):
        user_data = self.user_and_score_repository.get_user_data(username)
        if isinstance(user_data, UserDto):
            if password != user_data.password:  # user exist but wrong password
                return ErrorDto(2)
        return user_data

    def get_top_7_score(self, level):
        return self.user_and_score_repository.get_top_7_score(level)

    def get_my_high_score(self, username, level):
        high_score = self.user_and_score_repository.get_my_high_score(username, level)
        if len(high_score.scores) == 0:  # data tidak ada
            high_score.scores.append((0))
        return high_score

    def get_friend_high_score(self, username, level):

        return self.user_and_score_repository.get_friend_high_score(username, level)

    def get_friend_and_request(self, username):
        dto = self.user_and_score_repository.get_friend_and_request(username)
        my_friends = [list(x) for x in dto.friends]

        for i in range(len(my_friends)):
            my_friends[i][1] = (datetime.now() - datetime.strptime(my_friends[i][1], "%Y-%m-%d %X")).total_seconds()
        my_friends.sort(key=lambda x: x[1])
        for i in range(len(my_friends)):
            if my_friends[i][1] // 60 <= 5:
                my_friends[i][1] = f"Online"
            elif 5 < my_friends[i][1] // 60 <= 60:
                my_friends[i][1] = f"{int(my_friends[i][1] // 60)} minutes ago"
            elif 0 < my_friends[i][1] // 3600 <= 24:
                my_friends[i][1] = f"{int(my_friends[i][1] // 3600)} hours ago"
            else:
                my_friends[i][1] = f"{int(my_friends[i][1] // 86400)} days ago"

        updated_dto = FriendAndRequestDto(my_friends, dto.friend_request)
        return updated_dto

    def check(self, username, friend_username):
        return self.user_and_score_repository.check_request(username, friend_username)

    def insert_new_request(self, from_, to_):
        self.user_and_score_repository.insert_new_request(from_, to_)

    def delete_request(self, from_, to_):
        self.user_and_score_repository.delete_request(from_, to_)

    def add_friend(self, username, new_friend):
        self.user_and_score_repository.add_friend(username, new_friend)

    def update_online_time(self, username):
        self.user_and_score_repository.update_online_time(username)

    def get_query(self):
        min_score = []
        for i in range(1, 11):
            level_details = self.level_repository.get_level_details(i)
            min_score.append(level_details.min_score)
        score_dto = self.user_and_score_repository.query_score_per_user_and_level()
        scores = [[] for i in range(10)]
        for level, score in score_dto.scores:
            scores[level-1].append(score)
        return AverageQuery(min_score, scores)
