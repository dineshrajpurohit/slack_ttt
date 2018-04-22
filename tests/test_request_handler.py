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
        self.assertIn('can accept a challenge', response['body'])


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
        self.assertIn('can decline the current game', response['body'])

    def test_valid_next_move(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('has made a move', response['body'])

    def test_invalid_next_move(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('Invalid move', response['body'])

    def test_next_move_wrong_opponent(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user3'],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('can make a move', response['body'])

    def test_game_complete(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('has won the game', response['body'])

    def test_game_tie(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user2'],
                  'command': ['/ttt-move'],
                  'text': ['b2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt-move')
        self.assertIn('game is a tie', response['body'])

if __name__ == '__main__':
    unittest.main()
