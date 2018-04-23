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

        # print(sfdc.apexecute('handleTTTCommand', method='POST', data={'channelId':'ABC1234', 'requestor':'@user1', 'command':'/ttt'}))
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

    def new_game(self):
        response = self.__sfdc_rest_call('/ttt')
        return response['body']


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
        return response['body']

    def decline_game(self):
        response = self.__sfdc_rest_call('/ttt-decline')
        return response['body']

    def display_board(self):
        response = self.__sfdc_rest_call('/ttt-board')
        return response['body']

    def play_move(self):
        response = self.__sfdc_rest_call('/ttt-move')
        return response['body']

    def end_game(self):
        response = self.__sfdc_rest_call('/ttt-end')
        return response['body']


if __name__ == "__main__":
    s = SalesforceLogicSource()