from Scanner import Scanner
import json
import requests
import time

class Hate(Scanner):
    # returns an array of objects for entry into the log, or an empty array
    def scanObject(self, datasetID, documentID, docObject):
        notifications = []
        items = []
        itemsFlagged = False
        for key in docObject:
            # FIXME - Also iterate attributes that are themselves hierarchical sub-structures
            # Just a basic test here, to be replaced with appropriate document scanning
            print(key + ':' + str(docObject[key]))
            output = self.scanForHate(str(docObject[key]))
            if not output:
                # output is empty, no toxicity detected
                pass
            else:
                singleItem = {}
                singleItem['key'] = key
                singleItem['value'] = str(docObject[key])
                singleItem['toxicity'] = output
                #print(output)
                items.append(singleItem)
                itemsFlagged = True
        if itemsFlagged:
            singleNotification = self.__buildNotification(datasetID, documentID, items)
            notifications.append(singleNotification)

        return notifications


    def __buildNotification(self, datasetID, documentID, items):
        notification = {
            "job-type": "TOXICITY-NOTIFICATION",
            "submitted-by": "LDH-SCANNER",
            "modified": int(time.time()),
            "message": "This document was flagged as containing toxic text",
            "flags": items,
            "dataset": datasetID,
            "document": documentID,
            "status": "ALERT"
        }
        return notification


    def scanForHate(self, input):
        lang = self.config['lang']
        emotions, sentiment, toxicity, entities = self.extract_semiotic(self.testService(input, lang))
        return toxicity


    def testService(self, text: str, lang: str):
        #print("Processing: " + text + "\nin: " + lang)
        url = self.config['apiServer']
        user = self.config['apiUser']
        pwd = self.config['apiPassword']
        r = requests.post(url + lang + '/spice/analysis',
                          json={"content": text, "collection": "test"}, auth=(user, pwd))
        #print("Resp: " + str(r.json()))
        return r.json()


    def extract_semiotic(self, json):
        emotions = {}
        sentiment = {}
        toxicity = {}
        for semiotic in json['@graph'][0]['semiotics:denotes']:
            if semiotic['@id'].startswith("marl:"):
                s = semiotic['@id'].split(':')[1]
                lc = semiotic['orca:hasConfidenceLevel']['@value']
                sentiment[s] = lc if (sentiment.get(s) is None) else sentiment[s] + lc
            elif (semiotic['@type'].startswith('emotion:')):
                e = semiotic['@type'].split(":")[1]
                lc = semiotic['orca:hasConfidenceLevel']['@value']
                c = lc if (emotions.get(e) is None) else emotions[e] + lc
                emotions[e] = c
            elif (semiotic['@type'].startswith('toxicity:')):
                e = semiotic['@type'].split(":")[1]
                lc = semiotic['orca:hasConfidenceLevel']['@value']
                c = lc if (emotions.get(e) is None) else emotions[e] + lc
                toxicity[e] = c

        entities = {}
        for ann in json['@graph'][1:]:
            if ann['semiotics:denotes']['@id'].startswith('dbr:'):
                entities[ann['semiotics:denotes']['@id']] = {
                    '@types': ann['semiotics:denotes']['@types'],
                    'confidence': ann['semiotics:denotes']['orca:hasConfidenceLevel']['@value']
                }

        if (len(sentiment) > 1):
            print("Multiple Sentiment")
            sentiment = {"Neutral": 1}

        return emotions, sentiment, toxicity, entities
