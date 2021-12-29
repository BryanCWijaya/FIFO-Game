from FIFO.fifo_dtos import *
import sqlite3
from kink import inject

@inject
class LevelRepository:
    def __init__(self, db_select):
        if db_select == "old_db":
            db_file = './fifo.db'
            self.conn = sqlite3.connect(db_file)
            self.c = self.conn.cursor()
        elif db_select == "new_db":
            db_file = './fifo.db'
            self.conn = sqlite3.connect(db_file)
            self.c = self.conn.cursor()
            self.reset()
        elif db_select == "demo_db":
            db_file = "./fifo_demo.db"
            self.conn = sqlite3.connect(db_file)
            self.c = self.conn.cursor()
        elif db_select == "test":
            db_file = "./fifo_test.db"
            self.conn = sqlite3.connect(db_file)
            self.c = self.conn.cursor()
            self.reset()
        else:
            raise Exception("Invalid database selection")

    def reset(self):
        drop_all = "DROP TABLE  level_details"

        try:
            self.c.execute(drop_all)
        except:  # table not exist
            pass

        file = open('./sql_statement.txt')
        create_table = file.read().split('\n\n')
        for statement in create_table:
            if "level_details" in statement:
                self.c.execute(statement)

        self.conn.commit()

    def get_level_details(self, level):
        select_all_from_level = """
                SELECT *
                  FROM level_details
                 WHERE ID = ?
                """
        self.c.execute(select_all_from_level, (level,))
        level_details = self.c.fetchall()[0]
        dto = LevelDetailsDto(level_details[0], level_details[1], level_details[2], level_details[3], level_details[4],
                              level_details[5])
        return dto

@inject
class UserScoreRepository:
    def __init__(self, db_select):
        if db_select == "old_db":
            db_file = './fifo.db'
            self.conn = sqlite3.connect(db_file)
            self.c = self.conn.cursor()
        elif db_select == "new_db":
            db_file = './fifo.db'
            self.conn = sqlite3.connect(db_file)
            self.c = self.conn.cursor()
            self.reset()
        elif db_select == "demo_db":
            db_file = "./fifo_demo.db"
            self.conn = sqlite3.connect(db_file)
            self.c = self.conn.cursor()
        elif db_select == "test":
            db_file = "./fifo_test.db"
            self.conn = sqlite3.connect(db_file)
            self.c = self.conn.cursor()
            self.reset()
        else:
            raise Exception ("Invalid database selection")


    def reset(self):
        drop_all = [
            "DROP TABLE  friends;",
            "DROP TABLE  scores;",
            "DROP TABLE  users;",
            "DROP TABLE  friend_request"
        ]

        for statement in drop_all:
            try:
                self.c.execute(statement)
            except Exception as e:  # table not exist
                continue

        file = open('./sql_statement.txt')
        create_table = file.read().split('\n\n')
        for statement in create_table:
            if not "level_details" in statement:
                self.c.execute(statement)

        self.conn.commit()

    def add_new_user(self, username, email, password):
        insert_user_data = """
                INSERT INTO  users
                     VALUES  (?, ?, ?, 0, DATETIME('now', 'localtime'))
                """
        try:
            self.c.execute(insert_user_data, (username, email, password,))
        except sqlite3.IntegrityError:  # user already exist
            return ErrorDto(-2)
        self.conn.commit()

    def get_user_data(self, username):
        select_password_for_user = """
                SELECT  *
                  FROM  users
                 WHERE  username = ?
                """
        self.c.execute(select_password_for_user, (username,))
        user_details = self.c.fetchall()
        if len(user_details) == 0:
            return ErrorDto(1)
        else:
            return UserDto(user_details[0][0], user_details[0][1], user_details[0][2], user_details[0][3])

    def save_score(self, level, book_obtained, wrong_press, score, username):
        insert_score = """
                   INSERT INTO  scores
                        VALUES  (?, ?, ?, ?, ?)
                """
        self.c.execute(insert_score, (username, level, book_obtained, wrong_press, score))
        self.conn.commit()

    def get_top_7_score(self, level):
        select_top_7_from_score = '''
                        SELECT  username, score 
                          FROM  scores 
                         WHERE  level = ?
                      ORDER BY  score DESC
                         LIMIT  7
                '''
        self.c.execute(select_top_7_from_score, (level,))
        top_7_score = self.c.fetchall()
        score_dto = ScoreDto(top_7_score)
        return score_dto

    def increment_level(self, username):
        select_current_level = '''
                        SELECT  level 
                          FROM  users 
                         WHERE  username = ?
                        '''
        self.c.execute(select_current_level, (username,))
        level = self.c.fetchall()[0][0]

        update_current_level = """
                        UPDATE  users
                           SET  level = ?
                         WHERE  username = ?
                        """
        self.c.execute(update_current_level, (level + 1, username))
        self.conn.commit()

    def get_my_high_score(self, username, level):
        select_highest_score_where_my_name = """
                        SELECT  score
                          FROM  scores
                         WHERE  username = ?
                           AND  level = ?
                      ORDER BY  score DESC
                         LIMIT  1
                """

        self.c.execute(select_highest_score_where_my_name, (username, level))
        high_score = self.c.fetchall()
        score_dto = ScoreDto(high_score)
        return score_dto

    def get_friend_high_score(self, username, level):
        select_friend_highest_score = """
                        SELECT  scores.username, MAX(scores.score)
                          FROM  scores
                    INNER JOIN  friends
                            ON  scores.username = friends.friend_username
                         WHERE  level = ?
                           AND  friends.username = ?
                      GROUP BY  scores.username
                      ORDER BY  scores.score DESC
                         LIMIT  5
                """

        self.c.execute(select_friend_highest_score, (level, username))
        username_and_high_score = self.c.fetchall()
        friend_score_dto = ScoreDto(username_and_high_score)
        return friend_score_dto

    def get_friend_and_request(self, username):
        select_my_friend = """
                        SELECT  friends.friend_username, users.last_online
                          FROM  friends
                    INNER JOIN  users
                            ON  friends.friend_username = users.username
                         WHERE  friends.username = ?
                """
        self.c.execute(select_my_friend, (username,))
        my_friend = self.c.fetchall()

        select_request_for_me = """
                        SELECT  from_
                          FROM  friend_request
                         WHERE  to_ = ?
                """
        self.c.execute(select_request_for_me, (username,))
        request_for_me = self.c.fetchall()

        friend_request_dto = FriendAndRequestDto(my_friend, request_for_me)
        return friend_request_dto

    def check_request(self, username, friend_username):
        check_if_friend_username_exist = """
                        SELECT  username
                          FROM  users
                         WHERE  username = ?
                    """

        self.c.execute(check_if_friend_username_exist, (friend_username,))
        is_exist = len(self.c.fetchall())

        check_if_already_requested = """
                        SELECT  from_
                          FROM  friend_request
                         WHERE  from_ = ?
                           AND  to_ = ?
                    """

        self.c.execute(check_if_already_requested, (username, friend_username,))
        already_requested = len(self.c.fetchall())

        check_dto = CheckRequestDto(is_exist, already_requested)
        return check_dto

    def insert_new_request(self, from_, to_):
        insert_new_friend = """
                   INSERT INTO  friend_request
                        VALUES  (?, ?)
                """

        self.c.execute(insert_new_friend, (from_, to_))
        self.conn.commit()

    def delete_request(self, from_, to_):
        delete_friend_request = """
                    DELETE FROM  friend_request
                          WHERE  from_ = ?
                            AND  to_ = ?
                """

        self.c.execute(delete_friend_request, (from_, to_))
        self.conn.commit()

    def add_friend(self, username, friend):
        insert_new_friend = """
                INSERT INTO  friends
                     VALUES  (?, ?)
                    """

        self.c.execute(insert_new_friend, (username, friend))
        self.c.execute(insert_new_friend, (friend, username))

        delete_friend_request = """
                            DELETE FROM  friend_request
                                  WHERE  from_ = ?
                                    AND  to_ = ?
                        """

        self.c.execute(delete_friend_request, (friend, username))
        self.conn.commit()

    def update_online_time(self, username):
        update_current_online = """
                                UPDATE  users
                                   SET  last_online = DATETIME('now', 'localtime')
                                 WHERE  username = ?
                                """
        self.c.execute(update_current_online, (username,))
        self.conn.commit()

    def get_email(self, username):
        select_email_where_username = """
                                SELECT  email
                                  FROM  users
                                 WHERE  username = ?
                            """

        self.c.execute(select_email_where_username, (username,))
        email = self.c.fetchall()
        email_dto = EmailDto(email)
        return email_dto

    def query_score_per_user_and_level(self):
        select_score_groupby_two_columns = """
                                        SELECT  level, AVG(score)
                                          FROM  scores
                                      GROUP BY  username, level
                                    """

        self.c.execute(select_score_groupby_two_columns)
        query = self.c.fetchall()
        query_dto = ScoreDto(query)
        return query_dto
