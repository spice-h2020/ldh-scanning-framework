from LDH import LDH
from Privacy import Privacy
from Hate import Hate
import json
import time

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

def getStatus():
    try:
        with open('status.json') as statusFile:
            status = json.load(statusFile)
    except:
        print("unable to open status.json, creating new status file")
        status = {}
    return status


def writeStatus(status):
    with open('status.json', 'w') as outfile:
        json.dump(status, outfile)


def main():
    ldh = LDH()

    '''
    Instantiate scanner modules here
    '''
    hate = Hate('hate_config.json')
    privacy = Privacy()

    '''
    Add scanner modules to scannerList
    '''
    scannerList = [privacy, hate]
    # scannerList = [privacy]


    status = getStatus()
    if 'lastRun' in status:
        timestamp = status['lastRun']
    else:
        timestamp = 0
    allResultsReturned = False
    page = 1
    processBeginTimestamp = int(time.time())

    
    # Repeat Activity Log calls for multiple pages until all results are returned
    while not allResultsReturned:
        try:
            alResponse = ldh.getALEntries(page, timestamp)
        except Exception as err:
            print(err)
            time.sleep(60)  # sleep for 60 seconds (1 minute)
        else:
            if int(alResponse['documentCount']) < int(alResponse['pagesize']):
                allResultsReturned = True
            # Loop through each activity log entry
            print('Got '+str(alResponse['documentCount'])+' entries')
            print('starting loop through AL entries')
            for alEntry in alResponse['results']:
                datasetID = alEntry['al:datasetId']
                documentID = alEntry['al:documentId']

                print(LINE_UP, end=LINE_CLEAR)
                print(datasetID+':'+documentID)

                documentTimestamp = alEntry['_timestamp']

                payload = alEntry['al:request']['al:payload']
                payloadObject = json.loads(payload)

                for scanner in scannerList:
                    try:
                        notifications = scanner.scanObject(datasetID, documentID, documentTimestamp, payloadObject)
                    except Exception as err:
                        print(err)
                    else:
                        # Generally, only one notification is generated per doc, but the facility exists to return many, hence the iteration loop
                        for notification in notifications:
                            # Push notifications back to LDH here, or comment out and just print to the screen for testing
                            response = ldh.pushNotification(notification)
            page += 1
            status['lastRun'] = processBeginTimestamp
            writeStatus(status)


if __name__ == "__main__":

    while True:
        main()
        print('waiting...')
        time.sleep(60)  # sleep for 60 seconds (1 minute)
        print(LINE_UP, end=LINE_CLEAR)
