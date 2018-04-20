import json
from .dynamo_db import DynamoDB

class RequestHandler:

    def __init__(self, params):
        self.params = params

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
        """Route methos to call appropriate methos based on the resource provided

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
        if not 'text' in self.params:
            return self.respond(None, 'Please invite an opponent to play with you. \
                                        Use command `/ttt @opponentName`')

        channel_id = self.params['channel_id'][0]
        challenger_name = '@'+self.params['user_name'][0]
        opponent_name = self.params['text'][0]

        if opponent_name == challenger_name:
            return self.respond(None, response='You cannot challenge yourself. Please select some other opponent.')

        ddb = DynamoDB()
        ddb.initialize_db()
        if(ddb.game_in_progress(channel_id)):
            return self.respond(None, response='A game is already in progress between {0} and {1}.\
                                       Please wait for the game to end or type /ttt-board to view status of the game'
                                .format(challenger_name, opponent_name))

        # start game
        ddb.create_new_game(channel_id, challenger_name, opponent_name, challenger_name)
        return self.respond(None, 'Starting a new game')


    def __game_help(self):
        """Help handler which provides information about the game and how to play it.

        :return:
        """
        return self.respond(None, 'Game Helper')
        print("HELPING")


    def __accept(self):
        """Accept request handler is called when the user accepts a challenge

        :return:
        """
        return self.respond(None, 'Accepting a new game')
        print("ACCEPTED")


    def __decline(self):
        """Decline request handler is called when the user declines a challenge

        :return:
        """
        print("DECLINE")
        return self.respond(None, 'Declining a new game')


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
        return self.respond(None, 'Move to position ' + position)


    def __end(self):
        """In case a user wants to end the game if they want to

        :return: message that the user quit the game
        """
        print("END GAME")
        return self.respond(None, 'End a new game')


    def __invalid_request(self):
        """Send a invalid response payload if there is any issue encountered with the request

        :return: Invalid response payload
        """
        print("invalif GAME")
        return self.respond(None, 'Invalid request')

