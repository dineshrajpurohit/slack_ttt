from slack_ttt.base_logic_source import BaseLogicSource
from .dynamo_db import DynamoDB
from slack_ttt.response_message import ResponseMessageBuilder as RMB
from datetime import datetime
import time
import logging
from slack_ttt.logger import setup_logging, log_entry_exit

setup_logging()
logger = logging.getLogger(__name__)

@log_entry_exit
class NativeLogicSource(BaseLogicSource):

    def initialize(self, params):
        self.ddb = DynamoDB()
        self.ddb.initialize_db()
        self.channel_id = params['channel_id'][0]
        self.requester = '@' + params['user_name'][0]
        self.command = None
        if 'text' in params:
            self.command = params['text'][0]

    @log_entry_exit
    def new_game(self):
        super().new_game()
        if self.command is None:
            return RMB.respond(None,
                               game_response_type='new_game_no_opponent',
                               values=[])

        if self.command == self.requester:
            return RMB.respond(None,
                               game_response_type='new_game_challenge_self',
                               values=[])

        current_game = self.ddb.current_game_state(self.channel_id)

        if 'Item' in current_game and current_game['Item']['game_status'] == 'in_progress':
            return RMB.respond(None,
                               game_response_type='new_game_in_progress',
                               values=[self.requester, self.command])

        # make sure new challenge is not made when there is a challenge pending from 30 mins
        if "Item" in current_game:
            current_game = current_game['Item']
            created_at = datetime.strptime(current_game['created_at'], "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            created_at_ts = time.mktime(created_at.timetuple())
            now_ts = time.mktime(now.timetuple())
            if ((now_ts - created_at_ts) / 60) < 5:
                return RMB.respond(None,
                                   game_response_type='new_game_new_challenge',
                                   values=[current_game['challenger_name'], current_game['opponent_name']])
        # start game
        new_game = self.ddb.create_new_game(self.channel_id,
                                            self.requester,
                                            self.command)

        if new_game is not None:
            return RMB.respond(None,
                               game_response_type='new_valid_game',
                               values=[self.requester, self.command, self.command],
                               slack_response_type='in_channel')
        else:
            print('Something went wrong when challenging for a game of tic-tac-toe')
            return RMB.respond(None,
                               game_response_type='err_response',
                               values=[])

    @log_entry_exit
    def game_help(self):
        super().game_help()
        """Help handler which provides information about the game and how to play it.

                :return:
                """
        return RMB.respond(None,
                           game_response_type='help_text',
                           values=[])

    @log_entry_exit
    def accept_game(self):
        super().accept_game()
        """Accept request handler is called when the user accepts a challenge

                    Conditions: The game can be only accepted by the opponent whom it was challenged to
                    Once the challenge is accepted the game a notification is publicly sent to the channel

                :return:
                """
        current_game = self.ddb.current_game_state(self.channel_id)

        # Use cases
        #   trying to accept a challenge with no game

        if not 'Item' in current_game or current_game['Item']['game_status'] == 'in_progress':
            return RMB.respond(None,
                               game_response_type='accept_no_challenge',
                               values=[])

        current_game = current_game['Item']
        #   Wrong opponent trying to accept the challenge
        if current_game['opponent_name'] != self.requester:
            return RMB.respond(None,
                               game_response_type='accept_wrong_player',
                               values=[current_game['opponent_name']])

        # right opponent trying to accept the challenge
        self.ddb.update_game(channel_id=self.channel_id, game_status='in_progress')
        response = '`{0}` has accepted the challenge by `{1}` to play tic-tact-toe\n' \
            .format(current_game['opponent_name'], current_game['challenger_name'])
        response += '{0} ( `{1}` ) vs {2} ( `{3}` )\n ' \
            .format(current_game['challenger_name'],
                    current_game['challenger_action'],
                    current_game['opponent_name'],
                    current_game['opponent_action'])
        response += '\n> next turn `{0}`\n\n'.format(current_game['current_turn_player'])
        response += self.draw_board()
        response += '\n> Play next move using command like eg. `/ttt-move b3` where `b` is row `3` is column in the grid'

        return RMB.respond(None,
                           game_response_type='',
                           values=[],
                           slack_response_type='in_channel',
                           response=response)

    @log_entry_exit
    def decline_game(self):
        super().decline_game()
        """Decline request handler is called when the user declines a challenge

                :return:
                """
        current_game = self.ddb.current_game_state(self.channel_id)
        if "Item" not in current_game:
            return RMB.respond(None,
                               game_response_type='decline_no_game',
                               values=[])

        if current_game['Item']['game_status'] == 'in_progress':
            return RMB.respond(None,
                               game_response_type='decline_game_in_progress',
                               values=[])

        current_game = current_game['Item']
        cg_challenger = current_game['challenger_name']
        cg_opponent = current_game['opponent_name']
        cg_status = current_game['game_status']

        # only game opponent can decline
        if cg_status == 'challenged':
            if cg_opponent == self.requester:
                self.ddb.delete_game(self.channel_id)
                return RMB.respond(None,
                                   game_response_type='decline_right_player',
                                   values=[cg_opponent, cg_challenger],
                                   slack_response_type='in_channel')
            else:
                return RMB.respond(None,
                                   game_response_type='decline_wrong_player',
                                   values=[cg_opponent])
        else:
            return RMB.respond(None,
                               game_response_type='err_response',
                               values=[])

    @log_entry_exit
    def display_board(self, response_type='Ephemeral'):
        """Board request handler displays the current status of the board to the user.

        :return: current view of the board
        """
        current_game = self.ddb.current_game_state(channel_id=self.channel_id)

        # if no game is being played
        if 'Item' not in current_game or current_game['Item']['game_status'] == 'challenged':
            return RMB.respond(None,
                               game_response_type='board_no_game',
                               values=[])

        current_game = current_game['Item']
        response = 'Current Status of the game: `{0}` ( `{1}` ) vs `{2}` ( `{3}` )'\
            .format(current_game['challenger_name'],
                    current_game['challenger_action'],
                    current_game['opponent_name'],
                    current_game['opponent_action'])
        response += '\n> Next turn `{0}` \n\n'.format(current_game['current_turn_player'])
        response += self.draw_board(current_game['loc_a1'],
                                      current_game['loc_a2'],
                                      current_game['loc_a3'],
                                      current_game['loc_b1'],
                                      current_game['loc_b2'],
                                      current_game['loc_b3'],
                                      current_game['loc_c1'],
                                      current_game['loc_c2'],
                                      current_game['loc_c3'],)
        return RMB.respond(None,
                           game_response_type='',
                           values=[],
                           slack_response_type=response_type,
                           response=response)

    @log_entry_exit
    def play_move(self):
        super().play_move()
        """Move handler handles the next move by the player.

                :param position: position where user wants to put X or O to
                :return: current view of the board after the move
                """
        # if there is no command
        if self.command is None:
            return RMB.respond(None,
                               game_response_type='move_no_position',
                               values=[])

        current_game = self.ddb.current_game_state(self.channel_id)

        if 'Item' not in current_game or current_game['Item']['game_status'] == 'challenged':
            return RMB.respond(None,
                               game_response_type='move_no_game',
                               values=[])

        current_game = current_game['Item']

        if current_game['current_turn_player'] != self.requester:
            return RMB.respond(None,
                               game_response_type='move_wrong_player',
                               values=[current_game['current_turn_player']])

        # check valid move
        if self.__check_valid_move(self.command, current_game):
            current_player = self.requester
            move = None
            next_player = current_player
            if current_player == current_game['challenger_name']:
                move = current_game['challenger_action']
                next_player = current_game['opponent_name']
            else:
                move = current_game['opponent_action']
                next_player = current_game['challenger_name']
            self.__update_db_with_move(self.command, move, next_player)

            # check if the last move won the game
            current_game = self.ddb.current_game_state(self.channel_id)
            current_game = current_game['Item']
            board = self.draw_board(current_game['loc_a1'],
                                      current_game['loc_a2'],
                                      current_game['loc_a3'],
                                      current_game['loc_b1'],
                                      current_game['loc_b2'],
                                      current_game['loc_b3'],
                                      current_game['loc_c1'],
                                      current_game['loc_c2'],
                                      current_game['loc_c3'])

            if self.__check_winner(current_game):
                response = RMB.response('game_won', [self.requester])

            # check if the last move was a tie
            elif self.__check_game_tie(current_game):
                response = RMB.response('game_tie', [current_game['challenger_name'],
                                                     current_game['opponent_name']])
            else:
                return self.display_board(response_type='in_channel')

            self.ddb.delete_game(self.channel_id)
            response += '`The final status of the board`\n\n'
            response += board
            return RMB.respond(None,
                               game_response_type='',
                               slack_response_type='in_channel',
                               values=[],
                               response=response)
        else:
            return RMB.respond(None,
                               game_response_type='move_invalid',
                               values=[])

    @log_entry_exit
    def end_game(self):
        super().end_game()
        """In case a user wants to end the game if they want to

                :return: message that the user quit the game
                """
        current_game = self.ddb.current_game_state(self.channel_id)
        if 'Item' not in current_game or current_game['Item']['game_status'] == 'challenged':
            return RMB.respond(None,
                               game_response_type='end_no_game',
                               values=[])

        current_game = current_game['Item']
        if self.requester == current_game['challenger_name'] or self.requester == current_game['opponent_name']:
            self.ddb.delete_game(self.channel_id)
            return RMB.respond(None,
                               game_response_type='end_game',
                               values=[self.requester],
                               slack_response_type='in_channel')
        else:
            return RMB.respond(None,
                               game_response_type='end_wrong_player',
                               values=[])

    def __check_valid_move(self, move, current_game):
        moves = {'a1': current_game['loc_a1'],
                 'a2': current_game['loc_a2'],
                 'a3': current_game['loc_a3'],
                 'b1': current_game['loc_b1'],
                 'b2': current_game['loc_b2'],
                 'b3': current_game['loc_b3'],
                 'c1': current_game['loc_c1'],
                 'c2': current_game['loc_c2'],
                 'c3': current_game['loc_c3'],
                 }
        if move in moves and moves[move] == 'None':
            return True
        else:
            return False

    def __update_db_with_move(self, move, val, next_player):
        if move == 'a1':
            self.ddb.update_game(channel_id=self.channel_id, loc_a1=val, current_turn_player=next_player)
        elif move == 'a2':
            self.ddb.update_game(channel_id=self.channel_id, loc_a2=val, current_turn_player=next_player)
        elif move == 'a3':
            self.ddb.update_game(channel_id=self.channel_id, loc_a3=val, current_turn_player=next_player)
        elif move == 'b1':
            self.ddb.update_game(channel_id=self.channel_id, loc_b1=val, current_turn_player=next_player)
        elif move == 'b2':
            self.ddb.update_game(channel_id=self.channel_id, loc_b2=val, current_turn_player=next_player)
        elif move == 'b3':
            self.ddb.update_game(channel_id=self.channel_id, loc_b3=val, current_turn_player=next_player)
        elif move == 'c1':
            self.ddb.update_game(channel_id=self.channel_id, loc_c1=val, current_turn_player=next_player)
        elif move == 'c2':
            self.ddb.update_game(channel_id=self.channel_id, loc_c2=val, current_turn_player=next_player)
        elif move == 'c3':
            self.ddb.update_game(channel_id=self.channel_id, loc_c3=val, current_turn_player=next_player)
        else:
            raise Exception()

    def __check_winner(self, current_game):

        # check winning play in rows
        if  current_game['loc_a1'] != 'None' \
                and current_game['loc_a1'] == current_game['loc_a2']\
                and current_game['loc_a1'] == current_game['loc_a3']:
            return True

        if current_game['loc_b1'] != 'None' \
                and current_game['loc_b1'] == current_game['loc_b2']\
                and current_game['loc_b1'] == current_game['loc_b3']:
            return True

        if current_game['loc_c1'] != 'None' \
                and current_game['loc_c1'] == current_game['loc_c2']\
                and current_game['loc_c1'] == current_game['loc_c3']:
            return True

        # check winning play in columns
        if current_game['loc_a1'] != 'None'\
                and current_game['loc_a1'] == current_game['loc_b1']\
                and current_game['loc_a1'] == current_game['loc_c1']:
            return True

        if current_game['loc_a2'] != 'None'\
                and current_game['loc_a2'] == current_game['loc_b2']\
                and current_game['loc_a2'] == current_game['loc_c2']:
            return True

        if current_game['loc_a3'] != 'None'\
                and current_game['loc_a3'] == current_game['loc_b3']\
                and current_game['loc_a3'] == current_game['loc_c3']:
            return True

        # check winning play diagonally
        if current_game['loc_a1'] != 'None'\
                and current_game['loc_a1'] == current_game['loc_b2']\
                and current_game['loc_a1'] == current_game['loc_c3']:
            return True

        if current_game['loc_a3'] != 'None'\
                and current_game['loc_a3'] == current_game['loc_b2']\
                and current_game['loc_a3'] == current_game['loc_c1']:
            return True

        return False

    def __check_game_tie(self, current_game):
        if current_game['loc_a1'] != 'None' \
            and current_game['loc_a2'] != 'None' \
            and current_game['loc_a3'] != 'None' \
            and current_game['loc_b1'] != 'None' \
            and current_game['loc_b2'] != 'None' \
            and current_game['loc_b3'] != 'None' \
            and current_game['loc_c1'] != 'None' \
            and current_game['loc_c2'] != 'None' \
            and current_game['loc_c3'] != 'None':
            return True
        return False


