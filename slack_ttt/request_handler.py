from datetime import datetime
from .dynamo_db import DynamoDB
import json
import time

class RequestHandler:

    def __init__(self, params):
        self.params = params
        self.ddb = DynamoDB()
        self.ddb.initialize_db()
        self.channel_id = params['channel_id'][0]
        self.requester = '@' + params['user_name'][0]
        self.command = None
        if 'text' in params:
            self.command = params['text'][0]

    @staticmethod
    def respond(err, response_type='Ephemeral', response=None):
        """This functions generates response based on info submitted by handler functions

        :param err: exception object if any kind of exception is raised
        :param res: response text to be sent back to slack
        :return: response json sent to slack
        """
        return {
            'statusCode': '400' if err else '200',
            'body': err.message if err else json.dumps(
                                                    {"response_type": response_type,
                                                     "text": response}),
            'headers': {
                'Content-Type': 'application/json',
            },
        }


    def route(self, resource):
        """Route method to call appropriate method based on the resource provided

        :param resource: the command which user made to the slack
        :return: response sent to slack
        """
        response = None
        if resource == '/ttt':
            response = self.__new_game()
        elif resource == '/ttt-help':
            response = self.__game_help()
        elif resource == '/ttt-accept':
            response = self.__accept()
        elif resource == '/ttt-decline':
            response = self.__decline()
        elif resource == '/ttt-board':
            response = self.__board()
        elif resource == '/ttt-move':
            response = self.__move()
        elif resource == '/ttt-end':
            response = self.__end()
        else:
            response = self.__invalid_request()
        return response

    def __new_game(self):
        """This request handler handles creation of new game with the provided opponent

        :param opponent: user with whom the new game will be played
        :return:
        """
        if self.command is None:
            return self.respond(None, response='Please invite an opponent to play with you.'
                                               ' Use command `/ttt @opponentName`')

        if self.command == self.requester:
            return self.respond(None, response='You cannot challenge yourself. Please select other opponent.')

        current_game = self.ddb.current_game_state(self.channel_id)

        if 'Item' in current_game and current_game['Item']['game_status'] == 'in_progress':
            return self.respond(None, response='A game is already in progress between `{0}` and `{1}`, '
                                               'Please wait for the game to end or type `/ttt-board` to view status of the game'
                                .format(self.requester, self.command))

        # make sure new challenge is not made when there is a challenge pending from 30 mins
        if "Item" in current_game:
            current_game = current_game['Item']
            created_at = datetime.strptime(current_game['created_at'], "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            created_at_ts = time.mktime(created_at.timetuple())
            now_ts = time.mktime(now.timetuple())
            if ((now_ts - created_at_ts) / 60) < 5:
                return self.respond(None, response="""A challenge was made recently by `{0}` to `{1}`. 
                Please wait for 5 minutes before new challenge can be made."""
                                    .format(current_game['challenger_name'], current_game['opponent_name']))

        # start game
        new_game = self.ddb.create_new_game(self.channel_id,
                                            self.requester,
                                            self.command)

        if new_game is not None:
            msg = '`{0}` has challenged `{1}` for a game of tic tac toe. \n `{2}` has 5 minutes to accept ' \
                  'the challenge by replying'\
                .format(self.requester, self.command, self.command)
            msg += ' `/ttt-accept` or decline the challenge by replying `/ttt-decline`'
            return self.respond(None, response_type='in_channel', response=msg)
        else:
            print('Something went wrong when challenging for a game of tic-tac-toe')
            return self.respond(None, response='Something went wrong')

    def __draw_board(self,
                         loc_a1='#',
                         loc_a2='#',
                         loc_a3='#',
                         loc_b1='#',
                         loc_b2='#',
                         loc_b3='#',
                         loc_c1='#',
                         loc_c2='#',
                         loc_c3='#'):

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



    def __game_help(self):
        """Help handler which provides information about the game and how to play it.

        :return:
        """
        help  = '*Tic-Tac-Toe Game Help*\n'
        help += 'Instruction on commands to play the game \n'
        help += '`/ttt @opponentusername` - challenge a game of ttt with the opponent.\n'
        help += '`/ttt-accept` - accept the challenge to play the game.\n'
        help += '`/ttt-decline` - decline challenge to play the game\n'
        help += '`/ttt-board` - display current status of the tic-tac-toe board\n'
        help += '`/ttt-move b3` - enter \'X\' or \'O\' at the specified location (row *b* and column *3*)\n'
        help += '`/ttt-help` - display help for the tic-tac-toe game\n'
        help += '`/ttt-end` - end the current game\n\n'
        help += '            `Board for Tic-Tac-Toe` \n\n'
        help += """```

                                   1      2      3
                                |------+------+------|
                             a  |  a1  |  a2  |  a3  |
                                |------+------+------|
                             b  |  b1  |  b2  |  b3  |
                                |------+------+------|
                             c  |  c1  |  c2  |  c3  |
                                |------+------+------|

                ```"""
        help += """ Rows are represented by letter `a`, `b` and `c` and columns are represented by number `1`, `2`, `3`.
         Every move user make should be combination of row and column location.
            e.g `/ttt-move b1`"""


        return self.respond(None, response=help)

    def __accept(self):
        """Accept request handler is called when the user accepts a challenge

            Conditions: The game can be only accepted by the opponent whom it was challenged to
            Once the challenge is accepted the game a notification is publicly sent to the channel

        :return:
        """
        current_game = self.ddb.current_game_state(self.channel_id)

        # Use cases
        #   trying to accept a challenge with no game

        if not 'Item' in current_game or current_game['Item']['game_status'] == 'in_progress':
            return self.respond(None, response='You have not been challenged for a game of tic-tac-toe yet. '
                                               'If you are interested in playing, challenge someone by typing '
                                               '`/ttt @opponentName`')

        current_game = current_game['Item']
        #   Wrong opponent trying to accept the challenge
        if current_game['opponent_name'] != self.requester:
            return self.respond(None, response='Only `{0}` can accept the challenge.'
                                .format(current_game['opponent_name']))

        # right opponent trying to accept the challenge
        self.ddb.update_game(channel_id=self.channel_id, game_status='in_progress')
        response = '`{0}` has accepted the challenge by `{1}` to play tic-tact-toe\n'\
            .format(current_game['opponent_name'], current_game['challenger_name'])
        response += '{0} ( `{1}` ) vs {2} ( `{3}` )\n '\
            .format(current_game['challenger_name'],
                    current_game['challenger_action'],
                    current_game['opponent_name'],
                    current_game['opponent_action'])
        response += '\n> next turn `{0}`\n\n'.format(current_game['current_turn_player'])
        response += self.__draw_board()
        response += '\n> Play next move using command like eg. `/ttt-move b3` where `b` is row `3` is column in the grid'

        return self.respond(None, response_type='in_channel', response=response)

    def __decline(self):
        """Decline request handler is called when the user declines a challenge

        :return:
        """
        current_game = self.ddb.current_game_state(self.channel_id)
        if "Item" not in current_game:
            return self.respond(None, response='`No current games exists.`')

        if current_game['Item']['game_status'] == 'in_progress':
            return self.respond(None, response='There is already a game in progress. '
                                      'If you are part of the game and dont\'t want to play anymore '
                                      'please type `/ttt-end` instead.')

        current_game = current_game['Item']
        cg_challenger = current_game['challenger_name']
        cg_opponent = current_game['opponent_name']
        cg_status = current_game['game_status']

        # only game opponent can decline
        if cg_status == 'challenged':
            if cg_opponent == self.requester:
                self.ddb.delete_game(self.channel_id)
                return self.respond(None,
                                    response_type='in_channel',
                                    response='{0} declined a challenge to play tic-tac-toe by {1}'
                                    .format(cg_opponent, cg_challenger))
            else:
                return self.respond(None, response='Only `{0}` can decline the challenge.'.format(cg_opponent))

        else:
            return self.respond(None, response='Something went wrong with your command. Please try again')

    def __board(self):
        """Board request handler displays the current status of the board to the user.

        :return: current view of the board
        """
        current_game = self.ddb.current_game_state(channel_id=self.channel_id)

        # if no game is being played
        if 'Item' not in current_game or current_game['Item']['game_status'] == 'challenged':
            return self.respond(None, response="""No tic-tac-toe game is being played currently. \
            If you are interested then you can challenge someone using command \n `/ttt @opponentName`""")

        current_game = current_game['Item']
        response = 'Current Status of the game: {0} ( {1} ) vs {2} ( {3} )'\
            .format(current_game['challenger_name'],
                    current_game['challenger_action'],
                    current_game['opponent_name'],
                    current_game['opponent_action'])
        response += '\n> Next turn {0} \n\n'.format(current_game['current_turn_player'])
        response += self.__draw_board()
        return self.respond(None, response=response)

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
        if move in moves and moves[move] is None :
            return True
        else:
            return False

    def __move(self):
        """Move handler handles the next move by the player.

        :param position: position where user wants to put X or O to
        :return: current view of the board after the move
        """
        # if there is no command
        if self.command is None:
            return self.respond(None, response='You have not provided a location for the move. \n'
                                               ' Use command `/ttt-move [location]')

        current_game = self.ddb.current_game_state(self.channel_id)

        if 'Item' not in current_game or current_game['Item']['game_status'] == 'challenged':
            return self.respond(None, response="""No tic-tac-toe game is being played currently. \
                        If you are interested then you can challenge someone using command \n `/ttt @opponentName`""")

        current_game = current_game['Item']

        if current_game['opponent_name'] != self.requester:
            return self.respond(None, response='Only `{0}` can play the next move in the game.'
                                .format(current_game['current_turn_player']))

        # check valid move
        if self.__check_valid_move(self.command, current_game):
            pass
        else:
            return self.respond(None, response='Invalid move. Please check the board by typing'
                                               ' `/ttt-board` for available moves.')


    def __end(self):
        """In case a user wants to end the game if they want to

        :return: message that the user quit the game
        """
        current_game = self.ddb.current_game_state(self.channel_id)
        if 'Item' not in current_game or current_game['Item']['game_status'] == 'challenged':
            return self.respond(None, response='`There are no current game being played`')

        current_game = current_game['Item']
        if self.requester == current_game['challenger_name'] or self.requester == current_game['opponent_name']:
            self.ddb.delete_game(self.channel_id)
            return self.respond(None,
                                response_type='in_channel',
                                response='`{0}` has ended the game.'.format(self.requester))
        else:
            return self.respond(None, response='Only the players who are currently playing can end the game')


    def __invalid_request(self):
        """Send a invalid response payload if there is any issue encountered with the request

        :return: Invalid response payload
        """
        return self.respond(None, response='Invalid request')

