from abc import abstractmethod
import pygame  # for square object


class Displayable:  # abstract method
    @abstractmethod
    def get_image(self):
        pass

    @abstractmethod
    def get_coordinate(self):
        pass

    @abstractmethod
    def get_size(self):
        pass

    @abstractmethod
    def update(self, value):
        pass


class Square(Displayable):
    def __init__(self):
        self.x_axis = 300
        self.y_axis = 225
        self.width = 200
        self.height = 200
        self.image = pygame.Rect(self.x_axis, self.y_axis, self.width, self.height)
        self.pos = 0  # 0 -> up, left, 1 -> down, left, 2 -> up, right, 3 -> down, right

    def get_image(self):
        return self.image

    def get_coordinate(self):
        return (self.x_axis, self.y_axis)

    def get_size(self):
        return (self.width, self.height)

    def update(self, pos):
        if pos == 0:
            self.x_axis = 300
            self.y_axis = 225
            self.width = 200
            self.height = 200
        elif pos == 1:
            self.x_axis = 535
            self.y_axis = 325
            self.width = 145
            self.height = 150
        elif pos == 2:
            self.x_axis = 694
            self.y_axis = 492
            self.width = 90
            self.height = 103
        elif pos == 3:
            self.x_axis = 122
            self.y_axis = 325
            self.width = 145
            self.height = 150
        self.image = pygame.Rect(self.x_axis, self.y_axis, self.width, self.height)

    def move_right_or_down(self):
        self.pos = (self.pos + 1) % 4
        self.update(self.pos)

    def move_left_or_up(self):
        self.pos = (self.pos - 1) % 4
        self.update(self.pos)


class Circle(Displayable):
    def __init__(self, level):
        self.x_axis = 91
        self.y_axis = 250
        self.size = 40
        self.pos = 0
        self.level = level

    def get_coordinate(self):
        return (self.x_axis, self.y_axis)

    def get_size(self):
        return self.size

    def update(self, pos):
        if pos == 0:
            self.x_axis = 91
            self.y_axis = 251
        elif pos == 1:
            self.x_axis = 248
            self.y_axis = 251
        elif pos == 2:
            self.x_axis = 405
            self.y_axis = 251
        elif pos == 3:
            self.x_axis = 562
            self.y_axis = 251
        elif pos == 4:
            self.x_axis = 719
            self.y_axis = 251
        elif pos == 5:
            self.x_axis = 91
            self.y_axis = 421
        elif pos == 6:
            self.x_axis = 248
            self.y_axis = 421
        elif pos == 7:
            self.x_axis = 405
            self.y_axis = 421
        elif pos == 8:
            self.x_axis = 562
            self.y_axis = 421
        elif pos == 9:
            self.x_axis = 718
            self.y_axis = 421

    def move_up_or_down(self):
        if (self.pos + 5) % 10 < self.level:
            self.pos = (self.pos + 5) % 10
            self.update(self.pos)

    def move_right(self):
        self.pos = (self.pos + 1) % self.level
        self.update(self.pos)

    def move_left(self):
        self.pos = (self.pos - 1) % self.level
        self.update(self.pos)

class LevelLock(Displayable):
    def __init__(self):
        self.image = pygame.image.load('./image/lock.png')
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.x_axis_for_each_level = [60, 217, 374, 531, 688, 60, 217, 374, 531, 688]
        self.y_axis_for_each_level = [220, 220, 220, 220, 220, 390, 390, 390, 390, 390]
        self.x_axis = 0
        self.y_axis = 0
        self.size = 80

    def get_image(self):
        return self.image

    def get_coordinate(self):
        return (self.x_axis, self.y_axis)

    def get_size(self):
        return self.size

    def update(self, value):
        self.x_axis = self.x_axis_for_each_level[value]
        self.y_axis = self.y_axis_for_each_level[value]

class BookPointer(Displayable):
    def __init__(self, start=0, end=5):
        self.start = start
        self.end = end
        self.x_axis = 20
        self.update(self.start)
        self.image = pygame.image.load('./image/icon.png')
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.pos = self.start

    def get_image(self):
        return self.image

    def get_coordinate(self):
        return (self.x_axis, self.y_axis)

    def update(self, pos):
        if pos == 0:
            self.y_axis = 200
        elif pos == 1:
            self.y_axis = 275
        elif pos == 2:
            self.y_axis = 350
        elif pos == 3:
            self.y_axis = 425
        elif pos == 4:
            self.y_axis = 500

    def get_size(self):
        return (self.image.get_width(), self.image.get_height())

    def move_up(self):
        self.pos = self.start + ((self.pos - 1 - self.start) % (self.end - self.start))
        self.update(self.pos)

    def move_down(self):
        self.pos = self.start + ((self.pos + 1 - self.start) % (self.end - self.start))
        self.update(self.pos)


class FriendBookPointer(BookPointer):
    def __init__(self, end= 5):
        super().__init__(end= end)
        self.x_axis = 510

    def update(self, pos):
        if pos == 0:
            self.y_axis = 260
        elif pos == 1:
            self.y_axis = 306
        elif pos == 2:
            self.y_axis = 352
        elif pos == 3:
            self.y_axis = 401
        elif pos == 4:
            self.y_axis = 448


class Book:  # not using Drawable interface because Book class digambar in BookStack Class, not in main screen
    def __init__(self, book, arrow, code):
        self.code = code
        self.book_body = book.copy()
        self.arrow = arrow
        self.combine()

    def combine(self):
        self.book_body.blit(self.arrow, (120, 25))

    def get_book(self):
        return self.book_body


class BigBook(Book):
    def __init__(self, book, arrow, code, strength):
        book = pygame.transform.scale(book, (book.get_width(), book.get_height() * 2))
        self.original_book = book.copy()
        super().__init__(book, arrow, code)
        self.strength = strength
        self.font = pygame.font.Font('./fonts/JerseyM54-aLX9.ttf', 40)
        text = self.font.render(str(self.strength) + 'x', False, (0, 0, 0))
        self.book_body.blit(text, (180, 75))

    def combine(self):
        self.book_body.blit(self.arrow, (120, 75))

    def hit(self):
        self.strength -= 1
        text = self.font.render(str(self.strength) + 'x', False, (0, 0, 0))
        self.book_body = self.original_book.copy()
        self.book_body = self.book_body.copy()
        self.book_body.blit(text, (180, 75))
        self.combine()

    def is_one_strength_left(self):
        if self.strength == 1:
            return True
        return False


class FadingBook(Book, Displayable):
    def __init__(self, book, arrow, code):
        super().__init__(book, arrow, code)
        self.alpha = 255
        self.size = (320, 101)
        self.x_axis = 220
        self.y_axis = 550 - book.get_height()

    def update(self, speed):
        if self.code == 0:
            self.y_axis -= speed
        if self.code == 1:
            self.x_axis += speed
        if self.code == 2:
            self.y_axis += speed
        if self.code == 3:
            self.x_axis -= speed
        self.alpha -= speed
        self.book_body.set_alpha(self.alpha)

    def is_disappear(self):
        if self.alpha <= 0:
            return True
        return False

    def get_image(self):
        return self.get_book()

    def get_size(self):
        return self.size

    def get_coordinate(self):
        return self.x_axis, self.y_axis


class BookStack(Displayable):
    def __init__(self, single_or_multi, books):
        self.books = books
        self.single_or_multi = single_or_multi  # 0 -> single player, 1 -> multiplayer left, 2 -> multiplayer right
        if self.single_or_multi == 0:
            self.coordinate = (220, -100)
        elif self.single_or_multi == 1:
            self.coordinate = (50, -100)
        elif self.single_or_multi == 2:
            self.coordinate = (350, -100)

        # make transparent surface
        self.surface = pygame.Surface((320, 700), pygame.SRCALPHA, 32)
        self.surface = self.surface.convert_alpha()

        self.surface_with_book = self.surface.copy()
        curr_height = 650
        for i in range(len(self.books)):
            if isinstance(self.books[i], BigBook):
                curr_height -= 200
            else:  # BigBook
                curr_height -= 100
            self.surface_with_book.blit(self.books[i].get_book(), (0, curr_height))

    def get_image(self):
        return self.surface_with_book

    def get_coordinate(self):
        return self.coordinate

    def get_size(self):
        return self.surface.get_width(), self.surface.get_height()

    def update(self, pop):
        if pop:
            popped_book = self.books.pop(0)
        self.surface_with_book = self.surface.copy()
        curr_height = 650
        for i in range(len(self.books)):
            if isinstance(self.books[i], BigBook):
                curr_height -= 200
            else:  # BigBook
                curr_height -= 100
            self.surface_with_book.blit(self.books[i].get_book(), (0, curr_height))
        if pop:
            return popped_book

    def is_empty(self):
        if len(self.books) == 0:
            return True
        else:
            return False


# unused yet
# class BookMeter(Displayable):
#     def __init__(self, image, single_or_multi):
#         self.single_or_multi = single_or_multi  # 0 -> single player, 1 -> multiplayer left, 2 -> multiplayer right
#         self.image = image
#         if self.single_or_multi == 0:
#             self.coordinate = (750, 20)
#         elif self.single_or_multi == 1:
#             self.coordinate = (250, 100)
#         elif self.single_or_multi == 2:
#             self.coordinate = (550, 100)
#         # make transparent surface
#         self.surface = pygame.Surface((47, 760), pygame.SRCALPHA, 32)
#         self.surface = self.surface.convert_alpha()
#
#     def get_image(self):
#         return self.surface_with_bookmeter
#
#     def get_coordinate(self):
#         return self.coordinate
#
#     def get_size(self):
#         return self.image.get_width, self.image.get_height
#
#     def update(self, value):
#         self.surface_with_bookmeter = self.surface
#         self.surface_with_bookmeter.blit(self.image, (0, -5))


class NormalText(Displayable):
    def __init__(self, string, font, center, hide=False):
        self.font = font
        self.text = string
        self.center = center
        self.hide = hide
        if hide == True:
            self.image = font.render("*" * len(string), True, (0, 0, 0))
        else:
            self.image = font.render(str(string), True, (0, 0, 0))
        self.coordinate = self.image.get_rect(center=center)

    def get_image(self):
        return self.image

    def get_text(self):
        return self.text

    def get_coordinate(self):
        return self.coordinate

    def set_coordinate(self, x, y):
        self.coordinate = self.text.get_rect(center=(x, y))

    def get_size(self):
        return self.font.size

    def update(self, new_string):
        self.text = new_string
        if self.hide:
            self.image = self.font.render("*" * len(new_string), True, (0, 0, 0))
        else:
            self.image = self.font.render(str(new_string), True, (0, 0, 0))
        self.coordinate = self.image.get_rect(center=self.center)

    def change_color_to_white(self):
        self.image = self.font.render(str(self.text), True, (255, 255, 255))

    def align_left(self):
        self.coordinate = self.center

    def align_right(self, x):
        self.coordinate = self.image.get_rect(y=self.center[1], right=x)


class FadingText(Displayable):
    def __init__(self, string, font):
        self.font = font
        self.string = string
        self.image = font.render(str(string), True, (0, 0, 0))
        self.coordinate = self.image.get_rect(center=(400, 300))
        self.alpha = 255

    def get_image(self):
        return self.image

    def get_coordinate(self):
        return self.coordinate

    def set_coordinate(self, x, y):
        self.coordinate = self.image.get_rect(center=(x, y))

    def get_size(self):
        return self.font.size

    def update(self, speed):
        self.alpha -= speed
        self.image.set_alpha(self.alpha)

    def is_disappear(self):
        if self.alpha <= 0:
            return True
        return False
