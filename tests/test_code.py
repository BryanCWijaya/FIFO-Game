from FIFO.fifo_service import FifoService
from FIFO.fifo_gui import Image
from FIFO.displayable import Displayable, Book
from FIFO.fifo_dtos import ErrorDto, UserDto
from kink import di

class MockBookStack(Displayable): # BookStack that cannot be displayed
    def __init__(self, single_or_multi, books):
        self.books = books
        self.single_or_multi = single_or_multi  # 0 -> single player, 1 -> multiplayer left, 2 -> multiplayer right

    def update(self, pop):
        if pop:
            popped_book = self.books.pop(0)
            return popped_book

    def is_empty(self):
        if len(self.books) == 0:
            return True
        else:
            return False

class MockBigBook(Book):
    def __init__(self, book, arrow, code, strength):
        super().__init__(book, arrow, code)
        self.strength = strength

def test_randomly_assign_book():
    di["db_select"] = "test"
    level = 7  # choose random level from 0 - 10
    image = Image()

    service1 = FifoService()
    level_data1 = service1.single_player_setup(image.colored_book, image.arrow_list, level, MockBigBook, MockBookStack)

    service2 = FifoService()
    level_data2 = service2.single_player_setup(image.colored_book, image.arrow_list, level, MockBigBook, MockBookStack)

    # should have same level, level_id, and min_score, but different book_stack
    assert level_data1.level == level_data2.level
    assert level_data1.level_id == level_data2.level_id
    assert level_data1.min_score == level_data2.min_score
    assert level_data1.book_stack != level_data2.book_stack

def test_should_pop_book():
    di["db_select"] = "test"
    level = 2
    image = Image()

    service = FifoService()
    level_data = service.single_player_setup(image.colored_book, image.arrow_list, level, MockBigBook, MockBookStack)
    book_stack = level_data.book_stack
    init_length = len(book_stack.books)
    key = book_stack.books[0].code
    service.stack_pop(book_stack, key)
    final_length = len(book_stack.books)

    assert final_length == init_length - 1

def test_login_with_correct_password():
    di["db_select"] = "test"
    service = FifoService()
    service.register_user("Bryan", "abc@def.gh", "12345678")
    user_data = service.verify_user("Bryan", "12345678")

    assert isinstance(user_data, UserDto)
    assert user_data.username == "Bryan"
    assert user_data.password == "12345678"
    assert user_data.email == "abc@def.gh"
    assert user_data.level == 0

def test_login_with_wrong_password():
    di["db_select"] = "test"
    service = FifoService()
    service.register_user("Bryan", "abc@def.gh", "12345678")
    user_data = service.verify_user("Bryan", "87654321")

    assert isinstance(user_data, ErrorDto)
    assert user_data.msg == 2

def test_should_return_my_high_score():
    di["db_select"] = "test"
    service = FifoService()
    service.setup("bryan", "abc@gmail.com", 4)

    service.level_finish(3, 0, 0, 100, 0)
    service.level_finish(3, 0, 0, 5000, 0)
    service.level_finish(3, 0, 0, 10, 0)
    service.level_finish(3, 0, 0, 6000, 0)
    service.level_finish(3, 0, 0, 7000, 0)
    service.level_finish(3, 0, 0, 4000, 0)
    service.level_finish(3, 0, 0, 1000, 0)
    service.level_finish(3, 0, 0, 2000, 0)
    service.level_finish(3, 0, 0, 2500, 0)
    service.level_finish(3, 0, 0, 3000, 0)

    my_high_score = service.get_my_high_score("bryan", 3).scores
    my_high_score = my_high_score[0]

    assert my_high_score[0] == 7000

def test_should_return_top_7_score():
    di["db_select"] = "test"
    service = FifoService()
    service.level_repository.reset()
    service.user_and_score_repository.reset()
    service.setup("Bryan", "abc@gmail.com", 4)

    service.level_finish(3, 0, 0, 100, 0)
    service.level_finish(3, 0, 0, 5000, 0)
    service.level_finish(3, 0, 0, 10, 0)
    service.level_finish(3, 0, 0, 6000, 0)
    service.level_finish(3, 0, 0, 7000, 0)
    service.level_finish(3, 0, 0, 4000, 0)
    service.level_finish(3, 0, 0, 1000, 0)
    service.level_finish(3, 0, 0, 2000, 0)
    service.level_finish(3, 0, 0, 2500, 0)
    service.level_finish(3, 0, 0, 3000, 0)

    top_7_score = service.get_top_7_score(3).scores
    top_7_score = [x[1] for x in top_7_score]
    assert top_7_score == [7000, 6000, 5000, 4000, 3000, 2500, 2000]

def test_should_get_request():
    di["db_select"] = "test"
    service = FifoService()

    service.insert_new_request("bryan", "sanga")
    dto = service.get_friend_and_request("sanga")
    friend_request = dto.friend_request

    assert friend_request[0][0] == "bryan"