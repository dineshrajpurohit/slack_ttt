import json


def respond(err, res=None):
    """This functions generates response based on info submitted by handler functions

    :param err: exception object if any kind of exception is raised
    :param res: response text to be sent back to slack
    :return: response json sent to slack
    """
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def new_game(opponent):
    """This request handler handles creation of new game with the provided opponent

    :param opponent: user with whom the new game will be played
    :return:
    """
    print("Starting a new game")
    return respond(None, 'Starting a new game')


def game_help():
    """Help handler which provides information about the game and how to play it.

    :return:
    """
    return respond(None, 'Game Helper')
    print("HELPING")


def accept():
    """Accept request handler is called when the user accepts a challenge

    :return:
    """
    return respond(None, 'Accepting a new game')
    print("ACCEPTED")


def decline():
    """Decline request handler is called when the user declines a challenge

    :return:
    """
    print("DECLINE")
    return respond(None, 'Declining a new game')


def board():
    """Board request handler displays the current status of the board to the user.

    :return: current view of the board
    """
    print("BOARD")
    return respond(None, 'Display current board')


def move(position):
    """Move handler handles the next move by the player.

    :param position: position where user wants to put X or O to
    :return: current view of the board after the move
    """
    print("MOVE")
    return respond(None, 'Move to position ' + position)


def end():
    """In case a user wants to end the game if they want to

    :return: message that the user quit the game
    """
    print("END GAME")
    return respond(None, 'End a new game')


def invalid_request():
    """Send a invalid response payload if there is any issue encountered with the request

    :return: Invalid response payload
    """
    print("invalif GAME")
    return respond(None, 'Invalid request')

