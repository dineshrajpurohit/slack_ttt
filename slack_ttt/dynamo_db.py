import boto3
import time

class Singleton:
    def __init__(self, class_):
        self.class_ = class_
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = self.class_(*args, **kwargs)
        return self.instance

@Singleton
class DynamoDB:
    ttt_table = None

    def __init__(self):
        pass

    def initialize_db(self):
        if self.ttt_table is None:
            self.ttt_table = boto3.resource('dynamodb').Table('ttt')

    def _construct_ddb_json(self,
                            channel_id,
                            challenger_name,
                            opponent_name,
                            current_turn_player,
                            loc_a1=None,
                            loc_a2=None,
                            loc_a3=None,
                            loc_b1=None,
                            loc_b2=None,
                            loc_b3=None,
                            loc_c1=None,
                            loc_c2=None,
                            loc_c3=None):
        """

        :param game_id_:
        :return:

        RESPONSE: {'ResponseMetadata': {'RequestId': 'BAOP7KQTA98N3T4QR52OAO0BVNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Thu, 19 Apr 2018 23:33:12 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2', 'connection': 'keep-alive', 'x-amzn-requestid': 'BAOP7KQTA98N3T4QR52OAO0BVNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2745614147'}, 'RetryAttempts': 0}}

        """
        return {
            'challenger_name': challenger_name,
            'opponent_name': opponent_name,
            'current_turn_player': current_turn_player,
            'channel_id': channel_id,
            'loc_a1': loc_a1,
            'loc_a2': loc_a2,
            'loc_a3': loc_a3,
            'loc_b1': loc_b1,
            'loc_b2': loc_b2,
            'loc_b3': loc_b3,
            'loc_c1': loc_c1,
            'loc_c2': loc_c2,
            'loc_c3': loc_c3,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def game_in_progress(self, channel_id):
        response = self.ttt_table.get_item(
            Key= { 'channel_id': channel_id }
        )
        if 'Item' in response:
            return True
        else:
            return False

    def current_game_state(self, challenge_id):
        """Get current state of the game

        :param challenge_id:
        :return:
        """
        return self.ttt_table.get_item({
            'key': challenge_id
        })['Item']

    def update_game(self):
        pass

    def create_new_game(self,
                        channel_id,
                        challenger_name,
                        opponent_name,
                        current_turn_player
                        ):

        response = self.ttt_table.put_item(
            Item= self._construct_ddb_json(
                                            channel_id=channel_id,
                                            challenger_name=challenger_name,
                                            opponent_name=opponent_name,
                                            current_turn_player=current_turn_player,
                                            loc_a1 = 'None',
                                            loc_a2 = 'None',
                                            loc_a3 = 'None',
                                            loc_b1 = 'None',
                                            loc_b2 = 'None',
                                            loc_b3 = 'None',
                                            loc_c1 = 'None',
                                            loc_c2 = 'None',
                                            loc_c3 = 'None'
                                        )
        )
        print('RESPONSE: ', response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def delete_game(self, game_id):
        """

        :param challenge_id: game id which needs to be deleted
        :return: response from dynamodb call
        """
        return self.ttt_table.delete_item({
            'key': game_id
        })


