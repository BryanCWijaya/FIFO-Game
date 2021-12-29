# import time
from math import ceil
from FIFO.tools import Displayer, Timer
from FIFO.displayable import *
from FIFO.fifo_service import *
import matplotlib.pyplot as plt


class Image:
    def __init__(self):
        self.sign_in_bg = pygame.image.load("./image/signin.jpg")
        self.sign_in_bg = pygame.transform.scale(self.sign_in_bg, (800, 600))
        self.sign_up_bg = pygame.image.load("./image/signup.jpg")
        self.sign_up_bg = pygame.transform.scale(self.sign_up_bg, (800, 600))
        self.main_menu_bg = pygame.image.load("./image/homepage.jpg")
        self.main_menu_bg = pygame.transform.scale(self.main_menu_bg, (800, 600))
        self.single_player_bg = pygame.image.load("./image/single player background.jpg")
        self.single_player_bg = pygame.transform.scale(self.single_player_bg, (800, 600))
        self.pause_bg = pygame.image.load("./image/pause.jpg")
        self.pause_bg = pygame.transform.scale(self.pause_bg, (800, 600))
        self.level_bg = pygame.image.load('./image/levels.jpg')
        self.level_bg = pygame.transform.scale(self.level_bg, (800, 600))
        red_book = pygame.image.load("./image/m.png")
        yellow_book = pygame.image.load("./image/k.png")
        green_book = pygame.image.load("./image/h.png")
        blue_book = pygame.image.load("./image/b.png")
        indigo_book = pygame.image.load("./image/n.png")
        purple_book = pygame.image.load("./image/u.png")
        self.colored_book = [red_book, green_book, blue_book, yellow_book, indigo_book, purple_book]
        arrow_up = pygame.image.load("./image/arrow-up.png")
        arrow_up = pygame.transform.scale(arrow_up, (50, 50))
        arrow_down = pygame.image.load("./image/arrow-down.png")
        arrow_down = pygame.transform.scale(arrow_down, (50, 50))
        arrow_left = pygame.image.load("./image/arrow-left.png")
        arrow_left = pygame.transform.scale(arrow_left, (50, 50))
        arrow_right = pygame.image.load("./image/arrow-right.png")
        arrow_right = pygame.transform.scale(arrow_right, (50, 50))
        self.arrow_list = (arrow_up, arrow_right, arrow_down, arrow_left)
        self.leaderboard_bg = pygame.image.load('./image/leaderboard_bg.jpg')
        self.leaderboard_bg = pygame.transform.scale(self.leaderboard_bg, (800, 600))
        self.friends_bg = pygame.image.load("./image/friend_bg.jpg")
        self.friends_bg = pygame.transform.scale(self.friends_bg, (800, 600))
        self.freeze = pygame.image.load("./image/freeze.jpg")
        self.freeze.set_alpha(100)

@inject
class FifoGui:
    def __init__(self, service: FifoService):
        self.service = service
        self.page = 0  # 0 -> main menu, 1 -> single player, 2 -> leaderboard, 3 -> friends

        pygame.init()  # initialize pygame

        self.screen = pygame.display.set_mode((800, 600))  # set window dimension
        self.displayer = Displayer(self.screen)

        # font, title and icon
        self.small_font = pygame.font.Font(pygame.font.get_default_font(), 25)
        self.font = pygame.font.Font('./fonts/JerseyM54-aLX9.ttf', 35)
        self.big_font = pygame.font.Font('./fonts/JerseyM54-aLX9.ttf', 150)
        pygame.display.set_caption('FIFO')
        icon = pygame.image.load('./image/icon.png')
        pygame.display.set_icon(icon)

        self.screen.fill((0, 0, 0))
        displayed_text = NormalText('Loading...', self.font, (400, 300))
        displayed_text.change_color_to_white()
        self.displayer.display(displayed_text)
        pygame.display.update()

        self.image = Image()  # load all self.image needed
        self.load_sound()  # load all sound needed

    def load_sound(self):
        self.wrong_fx = pygame.mixer.Sound('./sound/Wrong.mp3')
        self.countdown_fx = pygame.mixer.Sound('./sound/3_sec_countdown.wav')
        pygame.mixer.music.load('./sound/backsound.mp3')

    def run(self):
        user_data = self.signin()
        if user_data != -1:
            self.running = True
            self.service.setup(user_data.username, user_data.email, user_data.level)
        else:
            self.running = False
        while self.running:
            self.service.update_online_time(user_data.username)
            if self.page == 0:
                response = self.main_menu(user_data.username)
                if response == -1:
                    self.running = False
                elif response == -2:
                    user_data = self.signin()  # change user
                    if user_data != -1:
                        self.running = True
                        self.service.setup(user_data.username, user_data.email, user_data.level)
                    else:
                        self.running = False
                    continue
                else:
                    self.page = response
            elif self.page == 1:
                if user_data.level == 0:
                    level_data = self.service.single_player_setup(self.image.colored_book, self.image.arrow_list, 0,
                                                                  BigBook, BookStack)
                    status = self.tutorial(level_data.book_stack, level_data.level, level_data.min_score)
                    if status == -1:  # exit
                        self.running = False
                        break
                    user_data.level += 1
                    self.page = 1
                    continue
                response = self.select_level(user_data.level)
                if response == -1:
                    self.running = False
                elif response == -2:
                    self.page = 0
                else:
                    level = response + 1
                    while level <= 10:
                        self.service.update_online_time(user_data.username)
                        level_data = self.service.single_player_setup(self.image.colored_book, self.image.arrow_list,
                                                                      level, BigBook, BookStack)
                        status = self.single_player(level_data.book_stack, level_data.level_id, level_data.level,
                                                    level_data.min_score,
                                                    user_data.username)
                        if status == -1:  # exit
                            self.running = False
                            break
                        elif status == -2:  # restart
                            continue
                        elif status == 1:  # next level
                            level += 1
                            if level > user_data.level:
                                user_data.level += 1
                        else:  # change to another menu
                            self.page = status
                            break
                    else:
                        response = self.complete()
                        if response == -1:
                            self.running = False
                        else:
                            self.page = response
            elif self.page == 2:
                response = self.select_level(user_data.level)
                if response == -1:
                    self.running = False
                elif response == -2:
                    self.page = 0
                else:
                    level = response + 1
                    response_ = self.leaderboard(user_data.username, level)
                    if response_ == -1:
                        self.running = False
                    elif response_ == -2:
                        continue
            elif self.page == 3:
                response = self.show_friends(user_data.username)
                if response == -1:
                    self.running = False
                else:
                    self.page = response

    def main_menu(self, username):
        square = Square()
        username = NormalText(username, self.font, (115, 562))
        while True:
            self.displayer.display(self.image.main_menu_bg)
            self.displayer.display(square)
            self.displayer.display(username)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                        square.move_left_or_up()
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                        square.move_right_or_down()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if square.pos == 0:
                            return 1  # go to single player
                        elif square.pos == 1:
                            return 2  # go to leaderboards
                        elif square.pos == 2:
                            return -1  # quit
                        elif square.pos == 3:
                            return 3  # go to leaderboards
                    elif event.key == pygame.K_ESCAPE:
                        return -2  # change user (back to sign in)
            pygame.display.update()

    def tutorial(self, book_stack, level, min_score):
        self.show_level(level, 0)
        popped_books = []

        timer = Timer(60)
        disable_until = 60  # disable keyboard when wrong
        pygame.mixer.music.play()

        # score
        book_obtained = 0
        wrong_press = 0
        score = 0
        combo = 0
        displayed_score = NormalText("", self.font, (725, 30))
        displayed_tutor = NormalText("", self.font, (400, 100))
        while not book_stack.is_empty():
            self.displayer.display(self.image.single_player_bg)
            time_left = self.service.countdown(timer, 60, always_return=True)
            displayed_score.update(score)
            self.displayer.display(displayed_score)
            self.displayer.display(book_stack)
            if len(book_stack.books) == 1 and wrong_press == 0:
                displayed_tutor.update("Lets try pressing another arrow")
            elif disable_until <= time_left:
                displayed_tutor.update("You will be frozen for 2 second")
            else:
                if book_stack.books[0].code == 0:
                    displayed_tutor.update("Press UP arrow")
                elif book_stack.books[0].code == 1:
                    displayed_tutor.update("Press RIGHT arrow")
                elif book_stack.books[0].code == 2:
                    displayed_tutor.update("Press DOWN arrow")
                elif book_stack.books[0].code == 3:
                    displayed_tutor.update("Press LEFT arrow")
            self.displayer.display(displayed_tutor)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                if event.type == pygame.KEYDOWN:
                    if disable_until <= time_left:
                        break  # not accepting keyboard input
                    popped_book = None
                    if not (len(book_stack.books) == 1 and wrong_press == 0):
                        if event.key == pygame.K_UP:
                            popped_book = self.service.stack_pop(book_stack, 0)
                        if event.key == pygame.K_RIGHT:
                            popped_book = self.service.stack_pop(book_stack, 1)
                        if event.key == pygame.K_DOWN:
                            popped_book = self.service.stack_pop(book_stack, 2)
                        if event.key == pygame.K_LEFT:
                            popped_book = self.service.stack_pop(book_stack, 3)
                    elif book_stack.books[0].code == 0:
                        if event.key == pygame.K_RIGHT:
                            popped_book = self.service.stack_pop(book_stack, 1)
                        if event.key == pygame.K_DOWN:
                            popped_book = self.service.stack_pop(book_stack, 2)
                        if event.key == pygame.K_LEFT:
                            popped_book = self.service.stack_pop(book_stack, 3)
                    elif book_stack.books[0].code == 1:
                        if event.key == pygame.K_UP:
                            popped_book = self.service.stack_pop(book_stack, 0)
                        if event.key == pygame.K_DOWN:
                            popped_book = self.service.stack_pop(book_stack, 2)
                        if event.key == pygame.K_LEFT:
                            popped_book = self.service.stack_pop(book_stack, 3)
                    elif book_stack.books[0].code == 2:
                        if event.key == pygame.K_UP:
                            popped_book = self.service.stack_pop(book_stack, 0)
                        if event.key == pygame.K_RIGHT:
                            popped_book = self.service.stack_pop(book_stack, 1)
                        if event.key == pygame.K_DOWN:
                            popped_book = self.service.stack_pop(book_stack, 3)
                    elif book_stack.books[0].code == 3:
                        if event.key == pygame.K_UP:
                            popped_book = self.service.stack_pop(book_stack, 0)
                        if event.key == pygame.K_RIGHT:
                            popped_book = self.service.stack_pop(book_stack, 1)
                        if event.key == pygame.K_DOWN:
                            popped_book = self.service.stack_pop(book_stack, 2)

                    if isinstance(popped_book, Book):
                        book_obtained += 1
                        popped_books.append(FadingBook(popped_book.book_body, popped_book.arrow, popped_book.code))
                        score += 200 * (1 + (combo / 10))
                        combo += 1
                    elif popped_book == -1 and len(book_stack.books) == 1:  # wrong press
                        wrong_press += 1
                        disable_until = time_left - 2
                        self.wrong_fx.play()
                        combo = 0
                    elif popped_book == 0:
                        score += 100 * (1 + (combo / 10))
            if len(popped_books) != 0:
                if popped_books[0].is_disappear():
                    popped_books.pop(0)
                for i in range(len(popped_books)):
                    popped_books[i].update(3)
                    self.displayer.display(popped_books[i])

            pygame.display.update()
        pygame.mixer.music.stop()
        is_success = self.show_score(book_obtained, wrong_press, int(score), min_score)
        self.service.level_finish(0, book_obtained, wrong_press, score, is_success)
        return is_success

    def single_player(self, book_stack, level_id, level, min_score, username):
        self.show_level(level, min_score)
        popped_books = []

        # count = 0
        # start = time.time()

        timer = Timer(60)
        is_counting = False  # only count in last 3 second
        countdown = None
        is_waiting = True  # wait 3 second before start
        disable_until = 60  # disable keyboard when wrong
        pygame.mixer.music.play()

        # score
        book_obtained = 0
        wrong_press = 0
        score = 0
        combo = 0
        displayed_time = NormalText("", self.font, (60, 30))
        displayed_score = NormalText("", self.font, (725, 30))
        while not book_stack.is_empty() and countdown != 0:
            # if count % 100 == 1:  # 0.44 second, 0.10
            #     now = time.time()
            #     print('fps:', 100 / (now - start))
            #     start = now
            # count += 1
            self.displayer.display(self.image.single_player_bg)
            time_left = self.service.countdown(timer, 60, always_return=True)
            displayed_time.update(time_left)
            self.displayer.display(displayed_time)
            displayed_score.update(str(int(score)))
            self.displayer.display(displayed_score)
            self.displayer.display(book_stack)
            countdown = self.service.countdown(timer, 3)
            if countdown is not None:
                is_counting = True
                text = FadingText(countdown, self.big_font)
            if is_waiting:
                time_elapsed = self.wait_3_second(book_stack)
                if time_elapsed == -1:
                    return -1
                timer.update_start_time(time_elapsed)
                is_waiting = False
            if is_counting:
                text.update(2)
                self.displayer.display(text)
            if disable_until <= time_left:
                self.displayer.display(self.image.freeze)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        value = self.pause()
                        if value == 1:  # restart
                            pygame.mixer.music.stop()
                            return -2
                        elif value == 2:
                            return 0
                        elif value == -1:
                            return -1
                        else:
                            is_waiting = True
                            timer.update_start_time(value)
                            break
                    if disable_until <= time_left:
                        break  # not accepting keyboard input
                    popped_book = None
                    if event.key == pygame.K_UP:
                        popped_book = self.service.stack_pop(book_stack, 0)
                    if event.key == pygame.K_RIGHT:
                        popped_book = self.service.stack_pop(book_stack, 1)
                    if event.key == pygame.K_DOWN:
                        popped_book = self.service.stack_pop(book_stack, 2)
                    if event.key == pygame.K_LEFT:
                        popped_book = self.service.stack_pop(book_stack, 3)

                    if isinstance(popped_book, Book):
                        book_obtained += 1
                        popped_books.append(FadingBook(popped_book.book_body, popped_book.arrow, popped_book.code))
                        score += 200 * (1 + (combo / 10))
                        combo += 1
                    elif popped_book == -1:  # wrong press
                        wrong_press += 1
                        disable_until = time_left - 2
                        self.wrong_fx.play()
                        combo = 0
                    elif popped_book == 0:
                        score += 100 * (1 + (combo / 10))
            if len(popped_books) != 0:
                if popped_books[0].is_disappear():
                    popped_books.pop(0)
                for i in range(len(popped_books)):
                    popped_books[i].update(3)
                    self.displayer.display(popped_books[i])

            pygame.display.update()
        pygame.mixer.music.stop()
        is_success = self.show_score(book_obtained, wrong_press, int(score), min_score)
        if is_success == 0 or is_success == 1:
            self.service.level_finish(level_id, book_obtained, wrong_press, score, is_success)
        if is_success == 0:
            return -2
        else:
            return is_success

    def wait_3_second(self, visible_book_stack):
        timer = Timer(3)
        pygame.mixer.music.pause()
        self.countdown_fx.play()
        while True:
            self.displayer.display(self.image.single_player_bg)
            self.displayer.display(visible_book_stack)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
            countdown = self.service.countdown(timer, 3)
            if countdown is not None:
                if countdown == 0:
                    number = FadingText('GO', self.big_font)
                else:
                    number = FadingText(countdown, self.big_font)
            self.displayer.display(number)
            number.update(0.25)
            if countdown == -1:
                pygame.mixer.music.unpause()
                return timer.get_time_from_start()

            pygame.display.update()

    def pause(self):
        pygame.mixer.music.pause()
        timer = Timer()
        pointer = BookPointer(start=2, end=5)
        while True:
            self.displayer.display(self.image.pause_bg)
            self.displayer.display(pointer)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        pointer.move_up()
                    elif event.key == pygame.K_DOWN:
                        pointer.move_down()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if pointer.pos == 2:
                            time_elapsed = timer.get_time_from_start()
                            pygame.mixer.music.unpause()
                            return time_elapsed  # resume
                        elif pointer.pos == 3:
                            return 1  # restart
                        elif pointer.pos == 4:
                            return 2  # save and quit
            pygame.display.update()

    def show_level(self, level, min_score):
        timer = Timer(2)
        countdown = 2

        text = NormalText(level, self.big_font, (400, 300))
        text.change_color_to_white()
        text2 = NormalText(f"Get {min_score} to pass this level", self.font, (400, 400))
        text2.change_color_to_white()
        while countdown != 0:
            countdown = self.service.countdown(timer, 2)
            self.screen.fill((0, 0, 0))
            self.displayer.display(text)
            self.displayer.display(text2)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
            pygame.display.update()

    def show_score(self, book_obtained, wrong_press, score, min_score):
        labels = [NormalText("Book obtained", self.font, (250, 250)), NormalText("Wrong press", self.font, (250, 350)),
                  NormalText("Score", self.font, (250, 450))]
        values = [NormalText(0, self.font, (600, 250)), NormalText(0, self.font, (600, 350)),
                  NormalText(0, self.font, (600, 450))]
        success_or_fail = NormalText('', self.big_font, (400, 100))
        press_key = NormalText("Press any key to continue", self.font, (400, 540))
        press_key.change_color_to_white()
        plus = ceil(score / 750)
        for label in labels:
            label.change_color_to_white()
        timer = Timer(10)
        while True:
            self.screen.fill((0, 0, 0))
            for label in labels:
                self.displayer.display(label)
            for value in values:
                value.change_color_to_white()
                self.displayer.display(value)

            curr_time = timer.get_time_left()
            if 10 >= curr_time > 9:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return -1
            elif curr_time > 8:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return -1
                values[0].update(book_obtained)
            elif curr_time > 7:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return -1
                values[1].update(wrong_press)
            elif curr_time > 6:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return -1
                displayed_score = values[2].get_text()
                if displayed_score + plus < score:
                    values[2].update(displayed_score + plus)
                elif displayed_score < score:
                    values[2].update(score)
            elif curr_time > 5:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return -1
                if score >= min_score:
                    success_or_fail.update('SUCCESS')
                else:
                    success_or_fail.update('FAIL')
                success_or_fail.change_color_to_white()
                self.displayer.display(success_or_fail)
            else:
                self.displayer.display(success_or_fail)
                if int(curr_time) % 2 == 0:
                    self.displayer.display(press_key)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return -1
                    if event.type == pygame.KEYDOWN:
                        if score >= min_score:
                            return 1
                        else:
                            return 0
            pygame.display.update()

    def signin(self):
        data = [NormalText("", self.small_font, (591, 215)), NormalText("", self.small_font, (591, 289), hide=True),
                NormalText("", self.font, (400, 150))]  # username, password, msg
        pointer = BookPointer(end=2)
        while True:
            self.displayer.display(self.image.sign_in_bg)
            self.displayer.display(pointer)
            for i in data:
                self.displayer.display(i)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        user = self.signup()
                        if user == -1:
                            return -1
                        break
                    elif event.key == pygame.K_TAB:
                        average_dto = self.service.get_query()
                        plt.boxplot(average_dto.average_score)
                        plt.title("Average score for each level")
                        for i in range(1, 11):
                            plt.plot((i - 0.5, i + 0.5), (average_dto.min_score[i-1], average_dto.min_score[i-1]), "r")
                        plt.show()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        # check
                        if data[0].get_text() == "":
                            data[-1].update("Username must be filled")
                            break
                        elif data[1].get_text() == "":
                            data[-1].update("Password must be filled")
                            break
                        user_data = self.service.verify_user(data[0].get_text(), data[1].get_text())
                        if isinstance(user_data, ErrorDto):
                            if user_data.msg == 2:
                                data[-1].update("Wrong password")
                                break
                            elif user_data.msg == 1:
                                data[-1].update("User not registered, please sign up")
                                break
                        else:
                            return user_data
                    elif event.key == pygame.K_UP:
                        pointer.move_up()
                    elif event.key == pygame.K_DOWN:
                        pointer.move_down()
                    elif event.key == pygame.K_BACKSPACE:
                        selected = data[pointer.pos]
                        new_string = selected.get_text()[:-1]
                        selected.update(new_string)
                        data[-1].update('')
                    else:
                        try:
                            selected = data[pointer.pos]
                            new_string = selected.get_text() + chr(event.key)
                            selected.update(new_string)
                            data[-1].update('')
                        except:
                            selected = data[-1]
                            selected.update('Invalid Character')
            pygame.display.update()

    def signup(self):
        data = [NormalText("", self.small_font, (591, 215)), NormalText("", self.small_font, (591, 289)),
                NormalText("", self.small_font, (591, 363), hide=True),
                NormalText("", self.small_font, (591, 438), hide=True),
                NormalText("", self.font, (400, 150))]  # email, username, password, confirm pass, msg
        pointer = BookPointer(end=4)
        while True:
            self.displayer.display(self.image.sign_up_bg)
            self.displayer.display(pointer)
            for i in data:
                self.displayer.display(i)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 0
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        # check
                        if data[2].get_text() != data[3].get_text():
                            data[-1].update("Password doesn't match")
                            break
                        elif not 3 <= len(data[0].get_text()) <= 8:
                            data[-1].update("Username must be 3 until 8 characters")
                            break
                        elif data[1].get_text() == "":
                            data[-1].update("Email must be filled")
                            break
                        elif not 8 <= len(data[2].get_text()) <= 32 or not 8 <= len(data[3].get_text()) <= 32:
                            data[-1].update("Password must be 8 until 32 characters length")
                            break
                        else:
                            response = self.service.register_user(data[0].get_text(), data[1].get_text(),
                                                                  data[2].get_text())
                            if response is None:
                                data[-1].update("Your account has been created, please sign in")
                            elif response.msg == -2:
                                data[-1].update("Username already exist")
                            break
                    elif event.key == pygame.K_UP:
                        pointer.move_up()
                    elif event.key == pygame.K_DOWN:
                        pointer.move_down()
                    elif event.key == pygame.K_BACKSPACE:
                        selected = data[pointer.pos]
                        new_string = selected.get_text()[:-1]
                        selected.update(new_string)
                        data[-1].update('')
                    elif pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        selected = data[pointer.pos]
                        if event.key == pygame.K_2:
                            new_string = selected.get_text() + '@'
                            selected.update(new_string)
                            data[-1].update('')
                        elif event.key == pygame.K_MINUS:
                            new_string = selected.get_text() + '_'
                            selected.update(new_string)
                            data[-1].update('')
                        elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                            continue
                        else:
                            selected = data[-1]
                            selected.update('Invalid Character')
                    else:
                        try:
                            selected = data[pointer.pos]
                            new_string = selected.get_text() + chr(event.key)
                            selected.update(new_string)
                            data[-1].update('')
                        except:
                            selected = data[-1]
                            selected.update('Invalid Character')
            pygame.display.update()

    def complete(self):
        timer = Timer()
        self.screen.fill((0, 0, 0))
        text = 'Congratulation'
        text2 = 'You have done all level'
        displayed_text = NormalText('', self.font, (400, 275))
        displayed_text2 = NormalText('', self.font, (400, 325))
        press_key = NormalText("Press any key to continue", self.font, (400, 540))
        press_key.change_color_to_white()
        i = 0
        while True:
            time = timer.get_time_from_start() / 1000
            self.screen.fill((0, 0, 0))
            if time > 4:
                self.displayer.display(displayed_text)
                self.displayer.display(displayed_text2)
                if int(time) % 2 == 0:
                    self.displayer.display(press_key)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        return 0
                    elif event.type == pygame.QUIT:
                        return -1
            else:
                if time > i / 10:
                    i += 1
                    displayed_text.update(text[:i])
                    displayed_text2.update(text2[:max(0, i - 14)])
                    displayed_text.change_color_to_white()
                    displayed_text2.change_color_to_white()
                self.displayer.display(displayed_text)
                self.displayer.display(displayed_text2)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return -1
            pygame.display.update()

    def select_level(self, level):
        pointer = Circle(level)
        locks = [LevelLock() for i in range(10 - level)]
        for i in range(10 - level):
            locks[i].update(level + i)

        if level == 0:
            self.displayer.display(self.level_bg)
            for lock in locks:
                self.displayer.display(lock)
            pygame.display.update()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return -1
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return -2
        else:
            while True:
                self.displayer.display(self.image.level_bg)
                self.displayer.display(pointer)
                for lock in locks:
                    self.displayer.display(lock)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return -1
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            pointer.move_left()
                        elif event.key == pygame.K_RIGHT:
                            pointer.move_right()
                        elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                            pointer.move_up_or_down()
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            return pointer.pos
                        elif event.key == pygame.K_ESCAPE:
                            return -2
                pygame.display.update()

    def leaderboard(self, username, level):
        top_score_dto = self.service.get_top_7_score(level)
        top_score = top_score_dto.scores
        username_text = [NormalText(str(top_score[x][0]), self.font, (100, 46 + (65 * x))) for x in
                         range(len(top_score))]
        score_text = [NormalText(str(top_score[x][1]), self.font, (400, 46 + (65 * x))) for x in range(len(top_score))]
        my_highscore_dto = self.service.get_my_high_score(username, level)
        my_high_score = my_highscore_dto.scores
        try:
            my_high_score = NormalText(str(my_high_score[0][0]), self.font, (618, 95))
        except:
            my_high_score = NormalText(str(my_high_score[0]), self.font, (618, 95))
        my_high_score.change_color_to_white()
        friend_highscore_dto = self.service.get_friend_high_score(username, level)
        friend_highscore = friend_highscore_dto.scores
        friend_username_text = [NormalText(str(friend_highscore[x][0]), self.font, (575, 243 + (60 * x))) for x in
                                range(len(friend_highscore))]
        friend_score_text = [NormalText(str(friend_highscore[x][1]), self.font, (660, 220 + (60 * x))) for x in
                             range(len(friend_highscore))]

        for text in username_text + score_text:
            text.align_left()
        for text in score_text:
            text.align_right(388)
        for text in friend_score_text:
            text.align_right(740)
        while True:
            self.displayer.display(self.image.leaderboard_bg)
            self.displayer.display(my_high_score)
            for text in username_text + score_text + friend_username_text + friend_score_text:
                self.displayer.display(text)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return -2
            pygame.display.update()

    def show_friends(self, username):
        friend_and_request_dto = self.service.get_friend_and_request(username)
        my_friends = [x[0] for x in friend_and_request_dto.friends]
        my_friends_last_online = [x[1] for x in friend_and_request_dto.friends]
        if len(friend_and_request_dto.friend_request) > 0:
            my_request = [x[0] for x in friend_and_request_dto.friend_request]
        else:
            my_request = []
        displayed_friends = [NormalText(my_friends[x], self.font, (75, 111 + (47 * x))) for x in range(len(my_friends))]
        for disp in displayed_friends:
            disp.align_left()
        displayed_last_online = [NormalText(my_friends_last_online[x], self.small_font, (355, 133 + (47 * x))) for x in
                                 range(len(my_friends_last_online))]
        displayed_request = [NormalText(my_request[x], self.font, (550, 253 + (47 * x))) for x in
                             range(len(my_request))]
        for req in displayed_request:
            req.align_left()
        displayed_msg = NormalText("", self.font, (400, 40))
        book_pointer = FriendBookPointer(end=min(5, len(my_request)))
        search_for = NormalText("", self.font, (560, 111))
        search = True
        while True:
            self.displayer.display(self.image.friends_bg)
            self.displayer.display(displayed_msg)
            self.displayer.display(search_for)
            if search == False:
                self.displayer.display(book_pointer)
            for i in range(min(8, len(displayed_friends))):
                self.displayer.display(displayed_friends[i])
                self.displayer.display(displayed_last_online[i])
            for i in range(min(4, len(displayed_request))):
                self.displayer.display(displayed_request[i])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s and search == False:
                        displayed_msg.update("Moved to search user")
                        search = True
                        continue
                    elif event.key == pygame.K_TAB:
                        if len(my_request) > 0:
                            displayed_msg.update("Moved to friend request")
                            search = False
                        else:
                            displayed_msg.update("No friend request avilable")
                    elif event.key == pygame.K_ESCAPE:
                        return 0
                    if search == True:
                        if event.key == pygame.K_BACKSPACE:
                            new_string = search_for.get_text()[:-1]
                            search_for.update(new_string)
                            search_for.align_left()
                            displayed_msg.update('')
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            if not 3 <= len(search_for.get_text()) <= 8:
                                displayed_msg.update("Username must be 3-8 characters long")
                            elif search_for.get_text() == username:
                                displayed_msg.update("Can't add yourself")
                            elif search_for.get_text() in my_request:
                                displayed_msg.update(f"You already have friend request from {search_for.get_text()}")
                            else:
                                friend_username = search_for.get_text()
                                result = self.service.check(username, friend_username)
                                if friend_username in my_friends:
                                    displayed_msg.update(f"You already become friend with {friend_username}")
                                elif not result.is_exist:
                                    displayed_msg.update(f"User {friend_username} not found")
                                elif result.already_requested:
                                    displayed_msg.update(f"You already sent request to {friend_username}")
                                else:
                                    displayed_msg.update(f"Friend request sent to {friend_username}")
                                    self.service.insert_new_request(username, friend_username)
                        else:
                            try:
                                new_string = search_for.get_text() + chr(event.key)
                                if len(new_string) > 8:
                                    displayed_msg.update('Username cannot be more than 8 characters')
                                else:
                                    search_for.update(new_string)
                                    search_for.align_left()
                                    displayed_msg.update('')
                            except:
                                displayed_msg.update('Invalid Character')
                    else:
                        if event.key == pygame.K_UP:
                            book_pointer.move_up()
                        elif event.key == pygame.K_DOWN:
                            book_pointer.move_down()
                        elif event.key == pygame.K_c:
                            new_friend = my_request[book_pointer.pos]
                            self.service.add_friend(username, new_friend)
                            displayed_request.pop(book_pointer.pos)
                            my_request.pop(book_pointer.pos)
                            displayed_msg.update(f"You are now friends with {new_friend}")
                            if len(my_request) == 0:
                                search = True
                            book_pointer = FriendBookPointer(min(5, len(my_request)))
                        elif event.key == pygame.K_x:
                            new_friend = my_request[book_pointer.pos]
                            self.service.delete_request(new_friend, username)
                            displayed_request.pop(book_pointer.pos)
                            my_request.pop(book_pointer.pos)
                            displayed_msg.update(f"You reject {new_friend}\'s friend request")
                            if len(my_request) == 0:
                                search = True
                            book_pointer = FriendBookPointer(min(5, len(my_request)))
            pygame.display.update()
