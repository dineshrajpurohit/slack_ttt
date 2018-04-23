Tic-Tac-Toe on Slack (Serverless Architecture)
----------------------
This application is an implementation of basic Tic-Tac-Toe game on Slack. The user can initiate a challenge for the game of tic-tac-toe on slack channel.

##### Gameplay
Here are the list of command to be used to play the game:
* **/ttt @opponentUserName**: challenge a game of ttt with the opponent.
* **/ttt-accept**: accept the challenge to play the game.
* **/ttt-decline**: decline challenge to play the game
* **/ttt-board**: display current status of the tic-tac-toe board
* **/ttt-end**: end the current game
* **/ttt-move b3**: enter \'X\' or \'O\' at the specified location (row *b* and column *3*)
* **/ttt-help**: display help for the tic-tac-toe game

Here is what the Tic-Tac-Toe board looks like. 
* The rows are represented by letter **a**, **b** and **c**
* The columns are represented by number **1**, **2**, **3**
* The player uses combination or row and column to play the next ove.

                            1       2       3
                       |-------+-------+-------|
                     a |   #   |   #   |   #   |
                       |-------+-------+-------|
                     b |   #   |   #   |   #   |
                       |-------+-------+-------|
                     c |   #   |   #   |   #   |
                       |-------+-------+-------|
                       
                   

##### Technical Information

The application runs on AWS Lambda. The lambda functiona runs as a simple router which routes the logic bases on the configuration added.

The application has 2 major logic source which you can choose. The reason of this implementation was to create an application on AWS lambda using Python3 as native app or creating an integration between slack and Salesforce using AWS lambda as a route mechanism.
  
###### Python (Native implementation)
One of the implementation of the logic for this application is done using Python. The code/functionality resides on the lambda along with the router. 
Based on the value of the environment variable 'TTT_LOGIC_SOURCE', the factory class can redirect the logic implementation to the native implementation.

This implementation uses other component of AWS as follows:
* **API Gateway**: It is used in conjunction with Lambda where the slack slash commands are redirected to. When the user initiate a command which is sent to a specific endpoint on the API gateways, the router picks up the command and redirect it to the proper implementation.
* **Cloudwatch**: To log all the transactions happening in the game
* **Dynamo DB**: Where the state of the application is stored. It is a AWS nosql document DB.

###### Salesforce
Python lambda function works as message message broker when communicating with Salesforce and all the code logic resides on salesforce side.
The logic is implemented on Salesforce using Apex REST service which the router on lambda communicates with and sends the information received from Slack.
Salesforce then generates the response and send it back to the router which then send it back to the Slack.

This implementation is just a proof of concept of an integration of slack with Salesforce via AWS lambda.

##### Intallation Instruction

###### AWS
Here are some of the configuration which needs to be done in order to run the application successfully on AWS Lambda. 
* **Encryption Key**: create a new encryption key in AWS IAM
* **DynamoDB** Create a new DynamoDB table name it **ttt** and add **channel_id** as the primary key. Copy the ARN for AWS policy.
* **AWS IAM role**: Please create a new IAM role (name anything) and attach a policy from ttt_dynamodb.json file located in docs folder. (Make sure to go back and change all the ARN's in the policy json )
* **API Gateway**: Upload/copy the API swagger file from docs/api folder to API gateway.
* **Lambda function**: 
    * Create a new lambda function (Any name) and select runtime Python 3.6 and role from the existing role we created above. 
    * Once lambda function is created, go to API gateway and add lambda as integration type (choose proxy integration) and select the lambda function created above. Repeat this for all endpoints.
    * In lambda function attach the API gateway as trigger for lambda function. With your role setting you should be able to see cloudwatch and dynamodb as resource attached to lambda function.
    * Add all the environment variabled from setting.py into lambda. You can upload the entire code repo by creating a zip file and uploading as function package.
* **publish.sh**: helper bash script to auto generate zip file and push it to lambda using AWS CLI.
    
###### Salesforce
Here are list of file which needs to be created in your salesforce instance in order for it to work. These files are stored in docs/salesforce folder

