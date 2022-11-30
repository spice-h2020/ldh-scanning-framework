import json
import time

class Scanner:
    def __init__(self):
        # Initialisation code here...
        with open('scanner_config.json') as configFile:
            self.config = json.load(configFile)

    # returns an array of objects for entry into the log, or an empty array
    def scanObject(self, datasetID, documentID, docObject):
        itemsFound = False
        items = []
        # Loop through all the fields in the document
        for key in docObject:
            # Just a basic test here, to be replaced with appropriate document scanning
            if '@' in docObject[key]:
                # build an appropriate notification
                itemsFound = True
                message = 'An @ symbol was found, this may indicate a email address'
                items.append(self.__buildNotification(datasetID, documentID, key, docObject[key], message))
        return items


    def __buildNotification(self, datasetID, documentID, fieldName, fieldValue, message):
        notification = {
            "job-type": "SAMPLE-NOTIFICATION",
            "submitted-by": "LDH-SCANNER",
            "modified": int(time.time()),
            "message": message,
            "dataset": datasetID,
            "document": documentID,
            "field": fieldName,
            "value": fieldValue,
            "status": "ALERT"
        }
        return notification
