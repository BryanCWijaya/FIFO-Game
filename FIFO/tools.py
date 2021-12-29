from FIFO.displayable import Square, Circle, Displayable
import pygame
from math import ceil


class Displayer:  # class for drawing object to screen
    def __init__(self, screen):
        self.screen = screen

    def display(self, drawable):
        if isinstance(drawable, Square):
            pygame.draw.rect(self.screen, (255, 0, 0), drawable.get_image(), 4)
        elif isinstance(drawable, Circle):
            pygame.draw.circle(self.screen, (255, 0, 0), drawable.get_coordinate(), drawable.get_size(), 6)
        elif isinstance(drawable, Displayable):
            self.screen.blit(drawable.get_image(), drawable.get_coordinate())
        elif isinstance(drawable, pygame.Surface):
            self.screen.blit(drawable, (0, 0))


class Timer:
    def __init__(self, second=0):
        self.second = second
        self.current = second + 1
        self.start_time = pygame.time.get_ticks()

    def get_second_left(self):  # only return when entering new second
        time_left = ceil(self.second - ((pygame.time.get_ticks() - self.start_time) / 1000))
        if time_left == self.current:
            return None
        else:
            self.current = time_left
            return time_left

    def get_time_left(self):  # always return time left
        time_left = self.second - ((pygame.time.get_ticks() - self.start_time) / 1000)
        return round(time_left, 2)

    def get_time_from_start(self):
        return pygame.time.get_ticks() - self.start_time

    def update_start_time(self, time):
        self.start_time += time
