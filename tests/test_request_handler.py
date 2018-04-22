import unittest
from slack_ttt.dynamo_db import DynamoDB
from slack_ttt.request_handler import RequestHandler

class RequestHandlerTest(unittest.TestCase):

    def setUp(self):
       pass

    def tearDown(self):
        ddb = DynamoDB()
        ddb.initialize_db()

        ddb.delete_game('TESTCHANNEL')

    def test_new_game_no_opponent(self):
        params ={'channel_id': ['TESTCHANNEL'],
                 'user_name': ['user1']
                 }
        request = RequestHandler(params)
        response = request.route('/ttt')
        self.assertIn('Please invite an opponent to play with you', response['body'])

    def test_new_game_self_opponent(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user1'],
                  'command': ['/ttt'],
                  'text': ['@user1']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt')
        self.assertIn('You cannot challenge yourself', response['body'])

    def test_new_game_valid_opponent(self):
        params = {'channel_id': ['TESTCHANNEL'],
                  'user_name': ['user1'],
                  'command': ['/ttt'],
                  'text': ['@user2']
                  }
        request = RequestHandler(params)
        response = request.route('/ttt')
        self.assertIn('for a game of tic tac toe', response['body'])

    def test_new_game_in_progress_game(self):
        pass

    def test_new_game_challenged_game_before_5_minutes(self):
        pass

    def test_new_game_challenged_game_after_5_minutes(self):
        pass

    def test_new_game_when_already_running_game(self):
        pass

    def test_accept_game_right_opponent(self):
        pass

    def test_accept_game_wrong_opponent(self):
        params = {'channel_id': ['TESTCHANNEL'], 'user_name': ['user1']}


    def test_decline_game_right_opponent(self):
        pass

    def test_decline_game_wrong_opponent(self):
        pass

    def test_valid_next_move(self):
        pass

    def test_invalid_next_move(self):
        pass

    def test_next_move_right_opponent(self):
        pass

    def test_next_move_wrong_opponnt(self):
        pass

    def test_game_complete(self):
        pass

    def test_game_tie(self):
        pass

if __name__ == '__main__':
    unittest.main()
