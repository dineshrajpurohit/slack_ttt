import unittest
from slack_ttt.dynamo_db import DynamoDB
from slack_ttt.request_handler import RequestHandler

class RequestHandlerTest(unittest.TestCase):

    def setUp(self):
        self.ddb = DynamoDB()
        self.ddb.initialize_db()
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user1'],
                  'command': ['/ttt'],
                  'text': ['@user2']
                  }
        self.new_game_main_request = RequestHandler(params)
        self.new_game_main_response = self.new_game_main_request.route('/ttt')

    def tearDown(self):
        self.ddb.delete_game('TESTCHANNEL')
        game = self.ddb.current_game_state('TESTCHANNELCUST')
        if 'Item' in game:
            self.ddb.delete_game('TESTCHANNELCUST')

    # NEW GAME USE CASES

    def test_new_game_no_opponent(self):
        params ={'channel_id': ['TESTCHANNELCUST'],
                 'user_name': ['user1']
                 }
        request = RequestHandler(params)
        response = request.route('/ttt')
        self.assertIn('Please invite an opponent to play with you', response['body'])

    def test_new_game_self_opponent(self):
        params = {'channel_id': ['TESTCHANNELCUST'],
                  'user_name': ['user1'],
                  'command': ['/ttt'],
                  'text': ['@user1']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt')
        self.assertIn('You cannot challenge yourself', response['body'])

    def test_new_game_valid_opponent(self):
        self.assertIn('for a game of tic tac toe', self.new_game_main_response['body'])

    def test_new_game_in_progress_game(self):
        self.ddb.update_game(channel_id='TESTCHANNEL', game_status='in_progress')
        response = self.new_game_main_request.route('/ttt')
        self.assertIn('A game is already in progress', response['body'])

    def test_new_game_challenged_game_before_5_minutes(self):
        response = self.new_game_main_request.route('/ttt')
        self.assertIn('Please wait for 5 minutes', response['body'])

    def test_accept_game_no_game(self):
        self.ddb.delete_game('TESTCHANNEL')
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-accept'],
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-accept')
        self.assertIn('You have not been challenged for a game of tic-tac-toe yet', response['body'])

    # GAME ACCEPT USE CASES

    def test_accept_in_progress_game(self):
        response = self.ddb.update_game(channel_id='TESTCHANNEL', game_status='in_progress')
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-accept'],
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-accept')
        self.assertIn('You have not been challenged for a game of tic-tac-toe yet', response['body'])

    def test_accept_game_right_opponent(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-accept'],
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-accept')
        self.assertIn('has accepted the challenge', response['body'])

    def test_accept_game_wrong_opponent(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user3'],
                  'command': ['/ttt-accept'],
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-accept')
        self.assertIn('can accept the challenge', response['body'])

    # GAME DECLINE USE CASES

    def test_decline_game_right_opponent(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-decline'],
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-decline')
        self.assertIn('declined a challenge to play tic-tac-toe', response['body'])

    def test_decline_game_wrong_opponent(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user3'],
                  'command': ['/ttt-decline']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-decline')
        self.assertIn('can decline the challenge', response['body'])

    # DISPLAY BOARD TEST CASES

    def test_board_no_game(self):
        response = self.new_game_main_request.route('/ttt-board')
        self.assertIn('No tic-tac-toe game is being played currently', response['body'])

    def test_board_current_game(self):
        self.ddb.update_game(channel_id='TESTCHANNEL', game_status='in_progress')
        response = self.new_game_main_request.route('/ttt-board')
        self.assertIn('Current Status of the game:', response['body'])

    # GAME MOVES TEST CASES

    def test_move_with_no_game(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('No tic-tac-toe game is being played currently.', response['body'])

    def test_move_wrong_player(self):
        self.ddb.update_game(channel_id='TESTCHANNEL', game_status='in_progress')
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user3'],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('can play the next move in the game.', response['body'])

    def test_valid_next_move(self):
        current_game = self.ddb.current_game_state('TESTCHANNEL')
        current_game = current_game['Item']
        self.ddb.update_game(channel_id='TESTCHANNEL', game_status='in_progress')
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': [current_game['current_turn_player'][1:]],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('Current Status of the game', response['body'])

    def test_invalid_next_move(self):
        self.ddb.update_game(channel_id='TESTCHANNEL',
                             game_status='in_progress',
                             current_turn_player='@user2',
                             loc_a1='X',
                             loc_a2='O',
                             loc_a3='X',
                             loc_b1='O',
                             loc_b2='X',
                             loc_b3='O',
                             loc_c1='O',
                             loc_c2='X',
                             loc_c3='O')
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('Invalid move', response['body'])

    def test_next_move_wrong_opponent(self):
        self.ddb.update_game(channel_id='TESTCHANNEL', game_status='in_progress')
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user3'],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('can play the next move in the game', response['body'])

    # GAME COMPLETION TEST CASES

    def test_game_complete(self):
        self.ddb.update_game(channel_id='TESTCHANNEL',
                             game_status='in_progress',
                             current_turn_player='@user2',
                             loc_a1='X',
                             loc_a2='X',
                             loc_a3='X')
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('has won the game', response['body'])

    def test_game_tie(self):
        current_game = self.ddb.current_game_state('TESTCHANNEL')
        current_game = current_game['Item']
        self.ddb.update_game(channel_id='TESTCHANNEL',
                             game_status='in_progress',
                             loc_a1='X',
                             loc_a2='O',
                             loc_a3='X',
                             loc_b1='O',
                             loc_b3='O',
                             loc_c1='O',
                             loc_c2='X',
                             loc_c3='O')
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': [current_game['current_turn_player'][1:]],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('is a tie', response['body'])

    # GAME ENDING TEST CASES

    def test_no_game_ending(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-move'],
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-end')
        self.assertIn('There are no current game being played', response['body'])

    def test_current_players_ending(self):
        self.ddb.update_game(channel_id='TESTCHANNEL', game_status='in_progress')
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-move'],
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-end')
        self.assertIn('has ended the game', response['body'])

    def test_non_player_ending(self):
        self.ddb.update_game(channel_id='TESTCHANNEL', game_status='in_progress')
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user3'],
                  'command': ['/ttt-move'],
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-end')
        self.assertIn('Only the players who are currently playing can end', response['body'])

if __name__ == '__main__':
    unittest.main()
