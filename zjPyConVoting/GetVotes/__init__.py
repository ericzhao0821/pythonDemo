import logging
import json
import os
import datetime

from pymongo import MongoClient
import azure.functions as func

import pymsteams

cosmosdbURL = os.environ["cosmosDBURL"]

client = MongoClient(cosmosdbURL)

# Set database
db = client.vote_app_database_test_Azure

# initializing the votes collection
votes = db.votes

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Getting the results.')

    return_data = {}

    votes = db.votes

    Bob = 0
    Eric = 0
    Marry = 0
    Others = 0
    Demo01 = 0
    Total = 0

    Total = votes.find().count()
    Bob = votes.find({'VotedFor': 'Bob'}).count()
    Eric = votes.find({'VotedFor': 'Eric'}).count()
    Marry = votes.find({'VotedFor': 'Marry'}).count()
    Others = Total - Bob - Eric - Marry

    return_data['TotalVotes'] = Total
    return_data['Bob'] = Bob
    return_data['Eric'] = Eric
    return_data['Marry'] = Marry
    return_data['Others'] = Others
    
    return_data = json.dumps(return_data)

    teamsWebHook = os.environ['TeamsWebHook']

    teamsMsg = pymsteams.connectorcard(teamsWebHook)
    teamsMsg.title("Demo Voting Results !")

    teamsSection = pymsteams.cardsection()
    teamsSection.addFact('Timestamp:', datetime.datetime.now().strftime("%m/%d/%Y-%H:%M:%S"))
    teamsSection.addFact('TotalVotes :', Total)
    teamsSection.addFact('Bob :', Bob)
    teamsSection.addFact('Eric :', Eric)
    teamsSection.addFact('Marry :', Marry)
    teamsSection.addFact('Others :', Others)

    teamsMsg.addSection(teamsSection)
    teamsMsg.text("Greeting !")
    teamsMsg.send()

    return func.HttpResponse(body=return_data ,status_code=200)