import json

class ResponseMessageBuilder:

    __responses = {
        'new_game_no_opponent'      :   'Please invite an opponent to play with you. \n'
                                        'Use command `/ttt @opponentName`',

        'new_game_challenge_self'   :   'You cannot challenge yourself. Please select other opponent.',

        'new_game_in_progress'      :   'A game is already in progress between `{0}` and `{1}`, '
                                        'Please wait for the game to end or type `/ttt-board` to view status of the game',

        'new_game_new_challenge'    :   """A challenge was made recently by `{0}` to `{1}`. 
                                           Please wait for 5 minutes before new challenge can be made.""",

        'new_valid_game'            :   '`{0}` has challenged `{1}` for a game of tic tac toe. \n `{2}` has 5 minutes to accept '
                                        'the challenge by replying `/ttt-accept` or decline the challenge by replying `/ttt-decline`',

        'accept_no_challenge'       :   'You have not been challenged for a game of tic-tac-toe yet. '
                                        'If you are interested in playing, challenge someone by typing '
                                        '`/ttt @opponentName`',

        'accept_wrong_player'       :   'Only `{0}` can accept the challenge.',

        'accept_right_player'       :   '`{0}` has accepted the challenge by `{1}` to play tic-tact-toe\n '
                                        '{2} ( `{3}` ) vs {4} ( `{5}` )\n\n> next turn `{6}`\n\n',

        'accept_right_player_nt'    :   '\n> Play next move using command like eg. `/ttt-move b3` where `b` is row `3` is column in the grid',

        'decline_no_game'           :   '`No current games exists.`',


        'decline_game_in_progress'  :   'There is already a game in progress. '
                                        'If you are part of the game and dont\'t want to play anymore '
                                        'please type `/ttt-end` instead.',

        'decline_right_player'      :   '`{0}` declined a challenge to play tic-tac-toe by `{1}`',

        'decline_wrong_player'      :   'Only `{0}` can decline the challenge.',

        'board_no_game'             :   """No tic-tac-toe game is being played currently. \
            If you are interested then you can challenge someone using command \n `/ttt @opponentName`""",

        'board'                     :   'Current Status of the game: `{0}` ( `{1}` ) vs `{2}` ( `{3}` ) \n> Next turn `{4}` \n\n',

        'move_no_position'          :   'You have not provided a position for the move. \n'
                                        'Use command `/ttt-move [position]',

        'move_no_game'              :   """No tic-tac-toe game is being played currently. \
                                        If you are interested then you can challenge someone using command \n `/ttt @opponentName`""",

        'move_wrong_player'         :   'Only `{0}` can play the next move in the game.',

        'game_won'                  :   '`{0}` has won the game :fireworks: :fireworks: :sparkler: :tada: :confetti_ball: \n\n',

        'game_tie'                  :   'The game between `{0}` and `{1}` is a `Cat\'s Game.` \n',

        'move_invalid'              :   'Invalid move. Please check the board by typing'
                                        '`/ttt-board` for available moves.',

        'end_no_game'               :   '`There are no current game being played`',

        'end_game'                  :   '`{0}` has ended the game.',

        'end_wrong_player'          :   'Only the players who are currently playing can end the game',

        'err_response'              :   'Something went wrong',

        'help_text'                 :   '*Tic-Tac-Toe Game Help*\n'
                                        'Instruction on commands to play the game \n'
                                        '`/ttt @opponentusername` - challenge a game of ttt with the opponent.\n'
                                        '`/ttt-accept` - accept the challenge to play the game.\n'
                                        '`/ttt-decline` - decline challenge to play the game\n'
                                        '`/ttt-board` - display current status of the tic-tac-toe board\n'
                                        '`/ttt-move b3` - enter \'X\' or \'O\' at the specified location (row *b* and column *3*)\n'
                                        '`/ttt-help` - display help for the tic-tac-toe game\n'
                                        '`/ttt-end` - end the current game\n\n'
                                        '            `Board for Tic-Tac-Toe` \n\n'
                                        """```

                                   1      2      3
                                |------+------+------|
                             a  |  a1  |  a2  |  a3  |
                                |------+------+------|
                             b  |  b1  |  b2  |  b3  |
                                |------+------+------|
                             c  |  c1  |  c2  |  c3  |
                                |------+------+------|

                                        ```"""
                                        """ Rows are represented by letter `a`, `b` and `c` and columns are represented by number `1`, `2`, `3`.
                                        Every move user make should be combination of row and column location.
            e.g `/ttt-move b1`"""

    }

    @staticmethod
    def response(type, values):
        if type in ResponseMessageBuilder.__responses:

            return (ResponseMessageBuilder.__responses[type]).format(*values)
        else:
            return 'Invalid response type {}'.format(type)

    @staticmethod
    def respond(err,
                game_response_type,
                values,
                slack_response_type='Ephemeral',
                response=None):
        """This functions generates response based on info submitted by handler functions

        :param err: exception object if any kind of exception is raised
        :param game_response_type response type in game
        :param slack_response_type Ephemeral or in_channel
        :param response: response text to be sent back to slack
        :return: response json sent to slack
        """
        if response is None \
                and game_response_type in ResponseMessageBuilder.__responses:
            response = (ResponseMessageBuilder.__responses[game_response_type]).format(*values)

        return {
            'statusCode': '400' if err else '200',
            'body': err.message if err else json.dumps(
                {
                    "response_type": slack_response_type,
                    "text": response
                }),
            'headers': {
                'Content-Type': 'application/json',
            },
        }