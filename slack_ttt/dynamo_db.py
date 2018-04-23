import boto3
import time
import random

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
                            challenger_action=None,
                            opponent_action=None,
                            game_status=None,
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
            'challenger_action' : challenger_action,
            'opponent_name': opponent_name,
            'opponent_action': opponent_action,
            'game_status': game_status,
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

    def current_game_state(self, channel_id):
        """Get current state of the game

        :param challenge_id:
        :return:
        """
        response = self.ttt_table.get_item(
                Key= { 'channel_id': channel_id }
            )
        return response


    def update_game(self,
                    channel_id,
                    challenger_name=None,
                    opponent_name=None,
                    current_turn_player=None,
                    game_status=None,
                    loc_a1 = None,
                    loc_a2 = None,
                    loc_a3= None,
                    loc_b1 = None,
                    loc_b2 = None,
                    loc_b3 = None,
                    loc_c1 = None,
                    loc_c2 = None,
                    loc_c3 = None
                    ):
        update_attributes = {}
        update_expression = 'SET'
        if challenger_name is not None:
            update_expression+=' challenger_name=:challenger_name,'
            update_attributes[':challenger_name'] = challenger_name
        if opponent_name is not None:
            update_expression+=' opponent_name=:opponent_name,'
            update_attributes[':opponent_name'] = opponent_name
        if current_turn_player is not None:
            update_expression+=' current_turn_player=:current_turn_player,'
            update_attributes[':current_turn_player'] = current_turn_player
        if game_status is not None:
            update_expression+= ' game_status=:game_status,'
            update_attributes[':game_status'] = game_status
        if loc_a1 is not None:
            update_expression += ' loc_a1=:loc_a1,'
            update_attributes[':loc_a1'] = loc_a1
        if loc_a2 is not None:
            update_expression += ' loc_a2=:loc_a2,'
            update_attributes[':loc_a2'] = loc_a2
        if loc_a3 is not None:
            update_expression += ' loc_a3=:loc_a3,'
            update_attributes[':loc_a3'] = loc_a3
        if loc_b1 is not None:
            update_expression += ' loc_b1=:loc_b1,'
            update_attributes[':loc_b1'] = loc_b1
        if loc_b2 is not None:
            update_expression += ' loc_b2=:loc_b2,'
            update_attributes[':loc_b2'] = loc_b2
        if loc_b3 is not None:
            update_expression += ' loc_b3=:loc_b3,'
            update_attributes[':loc_b3'] = loc_b3
        if loc_c1 is not None:
            update_expression += ' loc_c1=:loc_c1,'
            update_attributes[':loc_c1'] = loc_c1
        if loc_c2 is not None:
            update_expression += ' loc_c2=:loc_c2,'
            update_attributes[':loc_c2'] = loc_c2
        if loc_c3 is not None:
            update_expression += ' loc_c3=:loc_c3,'
            update_attributes[':loc_c3'] = loc_c3

        response = self.ttt_table.update_item(
            Key={
                'channel_id': channel_id
            },
            UpdateExpression=update_expression[:-1],
            ExpressionAttributeValues=update_attributes
         )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def create_new_game(self,
                        channel_id,
                        challenger_name,
                        opponent_name,
                        ):
        action = {0: 'X', 1: 'O'}
        r = random.randint(0,1)
        challenger_action = action[r]
        opponent_action = None
        if r == 0:
            opponent_action = action[1]
            current_turn_player=challenger_name
        else:
            opponent_action = action[0]
            current_turn_player=opponent_name
        response = self.ttt_table.put_item(
            Item= self._construct_ddb_json(
                                            channel_id=channel_id,
                                            challenger_name=challenger_name,
                                            opponent_name=opponent_name,
                                            current_turn_player=current_turn_player,
                                            challenger_action = challenger_action,
                                            opponent_action = opponent_action,
                                            game_status='challenged',
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
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return self.current_game_state(channel_id)
        else:
            return None

    def delete_game(self, channel_id):
        """

        :param challenge_id: game id which needs to be deleted
        :return: response from dynamodb call
        """
        response = self.ttt_table.delete_item(Key= { 'channel_id': channel_id })
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False


