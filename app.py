from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
import json
from datetime import datetime, timedelta

from Database import DataBase

app = Flask(__name__)
CORS(app)
api = Api(app)

with open('example_data.txt') as json_file:
    example_data = json.load(json_file)


def strfdelta(tdelta):
    if tdelta < timedelta(0):
        result = 0
    else:
        result = (tdelta.days * 24 * 60 * 60) + tdelta.seconds

    return result


class ForumZad5(Resource):
    Example_JSON_wpis = [
        {"id": 1, "author_id": 1, "overriding_wpis_id": 0, "odpowiedzi_wpis_array": [2], "content": "Example_content"},
        {"id": 2, "author_id": 2, "overriding_wpis_id": 1, "odpowiedzi_wpis_array": [3, 4],
         "content": "Example_content2"},
        {"id": 3, "author_id": 1, "overriding_wpis_id": 2, "odpowiedzi_wpis_array": [], "content": "Example_content3"},
        {"id": 4, "author_id": 2, "overriding_wpis_id": 2, "odpowiedzi_wpis_array": [], "content": "Example_content4"}]

    Example_JSON_autor = [{"id": 1, "name": "Marek", "nazwisko": "Demkowicz", "Wpisy_autora_array": [1, 3]},
                          {"id": 2, "name": "Jan", "nazwisko": "Kowalski", "Wpisy_autora_array": [2, 4]}]

    def get(self, Example_JSON_wpis=Example_JSON_wpis, Example_JSON_autor=Example_JSON_autor):
        return json.dumps({"Example_JSON_wpis": Example_JSON_wpis, "Example_JSON_autor": Example_JSON_autor})

    def post(self, example_data=example_data):
        new_post = request.get_json()
        new_post["id"] = str(len(example_data["post"]) + 1)
        example_data['post'].append(new_post)

        with open('example_data.txt', 'w') as outfile:
            json.dump(example_data, outfile)

        return {'you sent:': new_post}


class Forum(Resource):

    def get(self, example_data=example_data):
        return json.dumps(example_data)

    def post(self, example_data=example_data):
        new_post = request.get_json()
        new_post["id"] = str(len(example_data["post"]) + 1)
        example_data['post'].append(new_post)

        with open('example_data.txt', 'w') as outfile:
            json.dump(example_data, outfile)

        return {'you sent:': new_post}


class FarmGame(Resource):
    def get(self):
        action = request.args.get('action', default="", type=str)
        farmId = str(request.args.get('farmId', default=0, type=int))

        if farmId is not 0:
            if DataBase().sqlSelectJson(farmId=farmId)['farmId']:
                gold = DataBase().sqlSelectJson(farmId=farmId)['gold']
                now = datetime.now()

                if action == "Sowing":
                    costOfSowing = DataBase().sqlSelectJson(farmId=farmId)['costOfSowing']

                    if gold >= costOfSowing:
                        StrTimeOFHarvest = now + timedelta(
                            seconds=DataBase().sqlSelectJson(farmId="1")['growTime'])
                        StrTimeOFHarvest.strftime("%d/%m/%Y %H:%M:%S")

                        DataBase().update(
                            """UPDATE Farms SET gold=?,timeOfsowing=?, timeOfharvest=?,isHarvested=? WHERE farmId= """ + farmId + """;""",
                            (gold - DataBase().sqlSelectJson(farmId=farmId)['costOfSowing'],
                             now.strftime("%d/%m/%Y %H:%M:%S"), StrTimeOFHarvest.strftime("%d/%m/%Y %H:%M:%S"), 0)
                        )
                        dumpsJson = DataBase().sqlSelectJson(farmId=farmId)

                        RemainingTime = datetime.strptime(dumpsJson['timeOfHarvest'],
                                                          "%d/%m/%Y %H:%M:%S") - now

                        dumpsJson["RemainingTime"] = strfdelta(RemainingTime)
                        return json.dumps(dumpsJson)
                    else:

                        dumpsJson = DataBase().sqlSelectJson(farmId=farmId)

                        RemainingTime = datetime.strptime(dumpsJson['timeOfHarvest'],
                                                          "%d/%m/%Y %H:%M:%S") - now

                        dumpsJson["RemainingTime"] = strfdelta(RemainingTime)

                        return json.dumps(dumpsJson)


                elif action == "harvest":

                    if now > datetime.strptime(DataBase().sqlSelectJson(farmId="1")['timeOfSowing'],
                                               "%d/%m/%Y %H:%M:%S") + timedelta(
                        seconds=DataBase().sqlSelectJson(farmId="1")['growTime']):
                        DataBase().update(
                            """UPDATE Farms SET gold=?, isHarvested=? WHERE farmId= """ + farmId + """;""",
                            (gold + DataBase().sqlSelectJson(farmId=farmId)['productionLimit'], 1
                             ))
                        dumpsJson = DataBase().sqlSelectJson(farmId=farmId)

                        RemainingTime = datetime.strptime(dumpsJson['timeOfHarvest'],
                                                          "%d/%m/%Y %H:%M:%S") - now

                        dumpsJson["RemainingTime"] = strfdelta(RemainingTime)
                        return json.dumps(dumpsJson)
                    else:
                        dumpsJson = DataBase().sqlSelectJson(farmId=farmId)

                        RemainingTime = datetime.strptime(dumpsJson['timeOfHarvest'],
                                                          "%d/%m/%Y %H:%M:%S") - now

                        dumpsJson["RemainingTime"] = strfdelta(RemainingTime)
                        return json.dumps(dumpsJson)

                elif action == 'UpdateFarm':

                    updateCost = DataBase().sqlSelectJson(farmId=farmId)['updateCost']
                    if gold <= updateCost:
                        dumpsJson = DataBase().sqlSelectJson(farmId=farmId)

                        RemainingTime = datetime.strptime(dumpsJson['timeOfHarvest'],
                                                          "%d/%m/%Y %H:%M:%S") - now

                        dumpsJson["RemainingTime"] = strfdelta(RemainingTime)
                        return json.dumps(dumpsJson)
                    else:
                        DataBase().update(
                            """UPDATE Farms SET gold=?,productionLimit=?, costOfsowing=? ,updateCost=?, growTime=?, isHarvested=? WHERE farmId= """ + farmId + """;""",
                            (gold - updateCost,
                             DataBase().sqlSelectJson(farmId=farmId)['productionLimit'] + 20,
                             DataBase().sqlSelectJson(farmId=farmId)['costOfSowing'] + 15,
                             DataBase().sqlSelectJson(farmId=farmId)['updateCost'] + 2,
                             DataBase().sqlSelectJson(farmId=farmId)['growTime'] + 10,
                             0))
                        dumpsJson = DataBase().sqlSelectJson(farmId=farmId)

                        RemainingTime = datetime.strptime(dumpsJson['timeOfHarvest'],
                                                          "%d/%m/%Y %H:%M:%S") - now

                        dumpsJson["RemainingTime"] = strfdelta(RemainingTime)

                        return json.dumps(dumpsJson)
                else:
                    dumpsJson = DataBase().sqlSelectJson(farmId=farmId)

                    RemainingTime = datetime.strptime(dumpsJson['timeOfHarvest'],
                                                      "%d/%m/%Y %H:%M:%S") - now

                    dumpsJson["RemainingTime"] = strfdelta(RemainingTime)

                    return json.dumps(dumpsJson)
            else:

                return "InvalidFarmID"
        else:
            return " FarmID = 0"


api.add_resource(Forum, '/Forum')
api.add_resource(FarmGame, '/FarmGame')
api.add_resource(ForumZad5, "/ForumZad5")

if __name__ == '__main__':
    app.run(debug=True)
