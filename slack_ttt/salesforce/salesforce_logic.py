from slack_ttt.base_logic_source import BaseLogicSource
from slack_ttt.response_message import ResponseMessageBuilder as RMB
from simple_salesforce import Salesforce
from settings import (
                        SFDC_USERNAME,
                        SFDC_PASSWORD,
                        SFDC_TOKEN
                    )

class SalesforceLogicSource(BaseLogicSource):

    def initialize(self, params):
        self.sfdc = Salesforce(username=SFDC_USERNAME,
                               password=SFDC_PASSWORD,
                               security_token=SFDC_TOKEN)

        self.channel_id = params['channel_id'][0]
        self.requester = '@' + params['user_name'][0]
        self.command = None
        if 'text' in params:
            self.command = params['text'][0]

    def __sfdc_rest_call(self, resource):
        return self.sfdc.apexecute('handleTTTCommand',
                                   method='POST',
                                   data={'resource': resource,
                                         'channelId': self.channel_id,
                                         'requestor':self.requester,
                                         'command': self.command
                                         })

    def __generate_response(self, response_map):
        print('*** RESPONSE: ',response_map);
        game_response_type = response_map['game_response_type']
        values = response_map['values'].split(',')
        slack_response_type = None
        if "slack_response_type" in response_map:
            slack_response_type = response_map["slack_response_type"]
        else:
            slack_response_type = 'Ephemeral'

        response = None
        if 'response' in response_map:
            response = response_map['response']

        return RMB.respond(None,
                           game_response_type=game_response_type,
                           values=values,
                           slack_response_type=slack_response_type,
                           response=response)



    def new_game(self):
        response = self.__sfdc_rest_call('/ttt')
        return self.__generate_response(response['body'])


    def game_help(self):
        super().game_help()
        """Help handler which provides information about the game and how to play it.

           :return:
        """
        return RMB.respond(None,
                               game_response_type='help_text',
                               values=[])

    def accept_game(self):
        response = self.__sfdc_rest_call('/ttt-accept')
        return self.__generate_response(response['body'])

    def decline_game(self):
        response = self.__sfdc_rest_call('/ttt-decline')
        return self.__generate_response(response['body'])

    def display_board(self):
        response = self.__sfdc_rest_call('/ttt-board')
        return self.__generate_response(response['body'])

    def play_move(self):
        response = self.__sfdc_rest_call('/ttt-move')
        return self.__generate_response(response['body'])

    def end_game(self):
        response = self.__sfdc_rest_call('/ttt-end')
        return self.__generate_response(response['body'])