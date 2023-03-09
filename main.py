from LDH import LDH
from Privacy import Privacy
#from Hate import Hate
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
    # scanner = Scanner()
    # hate = Hate('hate_config.json')
    privacy = Privacy()
    # scannerList = [scanner, privacy]
    # scannerList = [privacy]
    status = getStatus()
    if 'lastRun' in status:
        timestamp = status['lastRun']
    else:
        timestamp = 0
    allResultsReturned = False
    page = 0
    processBeginTimestamp = int(time.time())

    
    # Repeat Activity Log calls for multiple pages until all results are returned
    while not allResultsReturned:
        page += 1
        alResponse = ldh.getALEntries(page, timestamp)
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

            processingTimestamp = alEntry['_timestamp']

            payload = alEntry['al:request']['al:payload']
            payloadObject = json.loads(payload)
            # notifications = hate.scanObject(datasetID, documentID, payloadObject)
            # for notification in notifications:
            #     # Push notifications back to LDH here, or comment out and just print to the screen for testing
            #     #response = ldh.pushNotification(notification)
            #     print(notification)
            # status['lastRun'] = processBeginTimestamp
            notifications = privacy.scanObject(
                datasetID, documentID, processingTimestamp, payloadObject)
            for notification in notifications:
                # Push notifications back to LDH here, or comment out and just print to the screen for testing
                response = ldh.pushNotification(notification)
                # Pretty Print JSON
                # filesLen = notification['Fields']
                # if len(filesLen) != 0:
                #     json_formatted_str = json.dumps(notification, indent=4)
                #     print(json_formatted_str)

        status['lastRun'] = processBeginTimestamp
        writeStatus(status)


if __name__ == "__main__":

    while True:
        main()
        print('waiting...')
        time.sleep(60)  # sleep for 60 seconds (1 minute)
        print(LINE_UP, end=LINE_CLEAR)
