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
        elif resource == 'ttt-end':
            response = self.__end()
        else:
            response = self.__invalid_request()
        return response


    def __new_game(self):
        """This request handler handles creation of new game with the provided opponent

        :param opponent: user with whom the new game will be played
        :return:
        """
        print(self.params)
        if self.command is None:
            return self.respond(None, response='Please invite an opponent to play with you.'
                                               ' Use command `/ttt @opponentName`')

        if self.command == self.requester:
            return self.respond(None, response='You cannot challenge yourself. Please select other opponent.')

        if(self.ddb.game_in_progress(self.channel_id)):
            return self.respond(None, response='A game is already in progress between `{0}` and `{1}`, '
                                               'Please wait for the game to end or type `/ttt-board` to view status of the game'
                                .format(self.requester, self.command))

        # make sure new challenge is not made when there is a challenge pending from 30 mins
        current_game = self.ddb.current_game_state(self.channel_id)
        if "Item" in current_game:
            current_game = current_game['Item']
            created_at = datetime.strptime(current_game['created_at'], "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            created_at_ts = time.mktime(created_at.timetuple())
            now_ts = time.mktime(now.timetuple())
            print(now_ts, created_at_ts, ((now - created_at).days) / 60)
            if ((now_ts - created_at_ts) / 60) < 5:
                return self.respond(None, response="""A challenge was made recently by `{0}` to `{1}`. 
                Please wait for 5 minutes before new challenge can be made."""
                                    .format(current_game['challenger_name'], current_game['opponent_name']))

        # start game
        new_game = self.ddb.create_new_game(self.channel_id,
                                            self.requester,
                                            self.command,
                                            self.requester)

        if new_game is not None:
            print('NEW GAME')
            msg = '`{0}` has challenged `{1}` for a game of tic tac toe. \n `{2}` has 5 minutes to accept ' \
                  'the challenge by replying'\
                .format(self.requester, self.command, self.command)
            msg += ' `/ttt-accept` or decline the challenge by replying `/ttt-decline`'
            return self.respond(None, response_type='in_channel', response=msg)
        else:
            print('Something went wrong when challenging for a game of tic-tac-toe')
            return self.respond(None, 'Something went wrong')

    def __draw_board(self,
                         loc_a1=' ',
                         loc_a2=' ',
                         loc_a3=' ',
                         loc_b1=' ',
                         loc_b2=' ',
                         loc_b3=' ',
                         loc_c1=' ',
                         loc_c2=' ',
                         loc_c3=' '):

        board   =   """```

            Board for Tic-Tac-Toe \n
            Board Format:          \n\n
                        |-------+-----+-----|
                        |  {0}  |  {1}  |  {2}  |
                        |-------+-------+-------|
                        |  {3}  |  {4}  |  {5}  |
                        |-------+-------+-------|
                        |  {6}  |  {7}  |  {8}  |
                        |-------+-------+-------|

        * Each number denotes the positions on the Tic-Tac-Toe Board

        ```""".format(loc_a1, loc_a2, loc_a3, loc_b1, loc_b2, loc_b3, loc_c1, loc_c2, loc_c3)
        return board



    def __game_help(self):
        """Help handler which provides information about the game and how to play it.

        :return:
        """
        print("HELPER METHOD")
        help = '            `Board for Tic-Tac-Toe on Slack` \n\n'
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

        return self.respond(None, 'Accepting a new game')


    def __decline(self):
        """Decline request handler is called when the user declines a challenge

        :return:
        """
        if self.ddb.game_in_progress(self.channel_id):
            return self.respond(None, 'There is already a game in progress. '
                                      'If you are part of the game and want to not play anymore '
                                      'please type `/ttt-end` instead.')

        current_game = self.ddb.current_game_state(self.channel_id)
        if "Item" not in current_game:
            return self.respond(None, response='`No current games exists.`')
        current_game = current_game['Item']
        cg_challenger = current_game['challenger_name']
        cg_opponent = current_game['opponent_name']
        cg_status = current_game['game_status']

        # only game opponent can decline
        if cg_status == 'challenged':
            if cg_opponent == self.requester:
                return self.respond(None,
                                    response_type='in_channel',
                                    response='{0} declined a challenge to play tic-tac-toe by {1}'
                                    .format(cg_opponent, cg_challenger))
            else:
                return self.respond(None, response='Only `{0}` can decline the current game.'.format(cg_opponent))

        else:
            return self.respond(None, response='Something went wrong with your command. Please try again')


    def __board(self):
        """Board request handler displays the current status of the board to the user.

        :return: current view of the board
        """
        print("BOARD")
        return self.respond(None, 'Display current board')


    def __move(self):
        """Move handler handles the next move by the player.

        :param position: position where user wants to put X or O to
        :return: current view of the board after the move
        """
        print("MOVE")
        return self.respond(None, 'Move to position ')


    def __end(self):
        """In case a user wants to end the game if they want to

        :return: message that the user quit the game
        """
        print("END GAME")
        challenger_name = self.params['username'][0]

        return self.respond(None, 'End a new game')


    def __invalid_request(self):
        """Send a invalid response payload if there is any issue encountered with the request

        :return: Invalid response payload
        """
        print("invalif GAME")
        return self.respond(None, 'Invalid request')

