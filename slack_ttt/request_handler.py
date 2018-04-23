from .impl_logic_factory import ImplLogicFactory

class RequestHandler:

    def __init__(self, params):
        self.logic_source = ImplLogicFactory.get_logic_source()
        self.logic_source.initialize(params=params)

    def route(self, resource):
        """Route method to call appropriate method based on the resource provided

        :param resource: the command which user made to the slack
        :return: response sent to slack
        """
        response = None
        if resource == '/ttt':
            response = self.logic_source.new_game()
        elif resource == '/ttt-help':
            response =self.logic_source.game_help()
        elif resource == '/ttt-accept':
            response = self.logic_source.accept_game()
        elif resource == '/ttt-decline':
            response = self.logic_source.decline_game()
        elif resource == '/ttt-board':
            response = self.logic_source.display_board()
        elif resource == '/ttt-move':
            response = self.logic_source.play_move()
        elif resource == '/ttt-end':
            response = self.logic_source.end_game()
        return response