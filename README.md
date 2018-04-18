Tic-Tac-Toe on Slack
----------------------
This application is an implementation of basic Tic-Tac-Toe game on Slack. The user can use slash command to initiate a game or challenge an opponent. 

##### Technical Information
Since the position required the knowledge of development in Salesforce Environment, I have decided to use Apex REST services for this application. 

###### Python
The python application lambda can be used as two fold. Either a message broker which forwards the request to salesforce to process the tic-tac-toe game logic or to process the logic itself.
The switch to decide whether python is the source for logic or salesforce is determined by a config variable in settings.py file. 

###### Salesforce
Python lambda function works as message message broker when communicating with Salesforce and all the code logic resides on salesforce side.
On the salesforce side I have written REST services which handles the logic after being communicated by the broker.
