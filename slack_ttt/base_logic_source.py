from abc import ABC, abstractmethod

class BaseLogicSource(ABC):

    @abstractmethod
    def initialize(self, params):
        pass

    @abstractmethod
    def new_game(self):
        pass

    @abstractmethod
    def game_help(self):
        pass

    @abstractmethod
    def accept_game(self):
        pass

    @abstractmethod
    def decline_game(self):
        pass

    @abstractmethod
    def display_board(self):
        pass

    @abstractmethod
    def play_move(self):
        pass

    @abstractmethod
    def end_game(self):
        pass

    def draw_board(self,
                         loc_a1='#',
                         loc_a2='#',
                         loc_a3='#',
                         loc_b1='#',
                         loc_b2='#',
                         loc_b3='#',
                         loc_c1='#',
                         loc_c2='#',
                         loc_c3='#'):
        loc_a1 = '#' if loc_a1 == 'None' else loc_a1
        loc_a2 = '#' if loc_a2 == 'None' else loc_a2
        loc_a3 = '#' if loc_a3 == 'None' else loc_a3
        loc_b1 = '#' if loc_b1 == 'None' else loc_b1
        loc_b2 = '#' if loc_b2 == 'None' else loc_b2
        loc_b3 = '#' if loc_b3 == 'None' else loc_b3
        loc_c1 = '#' if loc_c1 == 'None' else loc_c1
        loc_c2 = '#' if loc_c2 == 'None' else loc_c2
        loc_c3 = '#' if loc_c3 == 'None' else loc_c3

        board   =   """```
                            1       2       3
                        |-------+-------+-------|
                      a |   {0}   |   {1}   |   {2}   |
                        |-------+-------+-------|
                      b |   {3}   |   {4}   |   {5}   |
                        |-------+-------+-------|
                      c |   {6}   |   {7}   |   {8}   |
                        |-------+-------+-------|

        ```""".format(loc_a1, loc_a2, loc_a3, loc_b1, loc_b2, loc_b3, loc_c1, loc_c2, loc_c3)
        return board
