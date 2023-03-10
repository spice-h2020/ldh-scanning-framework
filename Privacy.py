from Scanner import Scanner
import json
import requests
import time
import spacy
import datetime
import re
import en_core_web_sm

nlp = spacy.load("en_core_web_sm")


class Privacy(Scanner):
    def __filter_english_words(self, text):
        english_text = ''
        for char in text:
            if ord(char) < 128:
                english_text += char
        return english_text

    def __buildNotification(self, fieldName, fieldValue, piiType, piiValue, alertScore, ascoreName):
        notification = {
            "Field Name": fieldName,
            "Value": fieldValue,
            "PII Type": piiType,
            "PII Detected Value": piiValue,
            "PII Description": piiType+' was detected',
            "Alert Score": alertScore,
            "Alert Name": ascoreName,
        }
        return notification

    def __valueToCheckPii(self, value, nlp, key):

        regex_email = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        #regex_zip = r"\b\d{5}(?:-\d{4})?\b"
        regex_phone = r"^(?!.*(19[2-9][0-9]|20[0-9][0-9]|21[0-1][0-9]|212[0-3]))(?:\+972|0)(?:-| )?(?:5[02-9]-|\(?(?:77|79|1(?:[89]|[2-9]\d))\)?-?\d{3}-?\d{4}|(?:[2-9]|5[013-9]|6[1-9]|7[1-9]|8[1-5])\d{7}|\(?(?:20|21)\d{1}\)?-?\d{7}|\(?(?:2[57]|[3-9][2-9])\)?-?\d{7}|7[0-4]\d{7}|\(?(?:1(?:1|3|[68][0-9])|2(?:[02468]|[13579][0-9])|3(?:[013]|4[0-9]|5[1-9]|[689][0-9])|4(?:[013-9]|[2-8][0-9])|5(?:[0235679]|[14][0-9])|6(?:[013-9]|[2-8][0-9])|7(?:[012345689]|[38][0-9])|8(?:[01579]|[2-8][0-9])|9(?:[01345789]|[2-9][0-9]))\)?-?\d{6,8}|\(?(?:11|3[02-9]|[4-8]\d|9[24578])\)?-?\d{6,8})$"
        regex_visacard = r"\b(4\d{3}[\s]\d{4}[\s]\d{4}[\s]\d{4}|4\d{3}[-]\d{4}[-]\d{4}[-]\d{4}|4\d{3}[.]\d{4}[.]\d{4}[.]\d{4}|4\d{3}\d{4}\d{4}\d{4})\b"
        regex_mastercard = r"\b(5[1-5][0-9]{2}[-\s]?[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}|22[23][0-9]{12})\b"
        #regex_socialmedia = r"(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)"
        regex_ips = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        regex_postcode = r'[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}'
        #regex_street_address = r"\b(?!\d{4}\b)(?!\d{5,}\b)(?!\d{4}\sby\sand\b)\d+\s+[A-Za-z]+\s+[A-Za-z]+\b"
        #regex_date = r'(\d{4}-\d{2}-\d{2}|\d{3}T\d{2}:\d{2}:\d{2}|\d{2}\/\d{2}\/\d{4}|\d{2}-\d{2}-\d{4}|\d{2}\/\d{2}\/\d{2}|\d{2}-\d{2}-\d{2})'
        regex_dob = r"(?:\b(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s+)?\d{4}))"
        regex_age = r"\b(\d{1,2}\syears|age\s?of\s?\d{1,2})\b"

        pii = {}

        find_email = re.findall(regex_email, value)
        if find_email:
            pii['EMAIL'] = find_email
        # find_zip = re.findall(regex_zip, value)
        # if find_zip:
        #     pii['ZIP'] = find_zip
        find_phone = re.findall(regex_phone, value)
        if find_phone:
            pii['PHONE'] = find_phone
        find_visacard = re.findall(regex_visacard, value)
        if find_visacard:
            pii['VISACARD'] = find_visacard
        find_mastercard = re.findall(regex_mastercard, value)
        if find_mastercard:
            pii['MASTERCARD'] = find_mastercard
        # find_socialmedia = re.findall(regex_socialmedia, value)
        # if find_socialmedia:
        #     pii['SOCIALMEDIA'] = find_socialmedia
        find_ips = re.findall(regex_ips, value)
        if find_ips:
            pii['IPS'] = find_ips
        find_postcode = re.findall(regex_postcode, value)
        if find_postcode:
            pii['POSTCODE'] = find_postcode
        # find_street_address = re.findall(regex_street_address, value)
        # if find_street_address:
        #     pii['STREETADDRESS'] = find_street_address
        # find_date = re.findall(regex_date, value)
        # if find_date:
        #     pii['DATE'] = find_date
        find_dob = re.findall(regex_dob, value)
        if find_dob:
            pii['DATE OF BIRTH'] = find_dob
        find_age = re.findall(regex_age, value)
        if find_age:
            pii['AGE'] = find_age

        # if len(pii) == 0:
        #     doc = nlp(value)
        #     for ent in doc.ents:
        #         if ent.label_ in ["PERSON"]:
        #             pii[ent.label_] = ent.text
        if len(pii) == 0:
            return {"code": 400}
        else:
            return {"code": 200, "key": key, "data": pii}

    def scanObject(self, datasetID, documentID,  processingTimestamp, docObject):
        items = []
        EXTREME = 4
        HIGH = 3
        MEDIUM = 2
        LOW = 1
        ascore = 0
        ascoreName = ''

        alart_name = ['Low', 'Medium', 'High', 'Extreme']
        assigned_value = {
            "PERSON": 4,
            "CITY": 1,
            "NAME": 4,
            "ORG": 2,
            "GPE": 1,
            "LOC": 1,
            "VISACARD": 4,
            "PHONE": 4,
            "EMAIL": 4,
            # "STREETADDRESS": 3,
            "STAE": 1,
            "COUNTRY": 1,
            # "DATE": 1,
            # "ZIP": 2,
            "POSTCODE": 2,
            "IPS": 2,
            "AGE": 2,
            "MASTERCARD": 4,
            # "SOCIALMEDIA": 3,
            'DATE OF BIRTH': 2,

        }
        # flatten the docObject
        flatObject = super().flattenObject(docObject)
        for key in flatObject:
            if re.search(r'CREATEAT', key) or re.search(r'timestamp', key) or re.search(r'updated', key) or re.search(r"[#@$_]*[iI][dD]", key):
                continue
            valueToCheckPii = flatObject[key]
            valueToCheckPii = self.__filter_english_words(str(valueToCheckPii))
            if (valueToCheckPii == ''):
                continue

            valueToCheckPii = re.sub(
                r'\b(0\.\d{1,40}|\b(0\.[0-9]|[1-9]\.[0-9]{1,40}|10\.[0-9]{1,40}))\b', "", valueToCheckPii)
            valueToCheckPii = re.sub(
                r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", "", valueToCheckPii)

            try:
                values = self.__valueToCheckPii(str(valueToCheckPii), nlp, key)
            except:
                raise Exception('Error running PII analysis. PII scanning abandoned for this document.')
            # print(key, values)
            # print(values)
            if (values["code"] == 200):
                for index in values["data"]:
                    if index in assigned_value:
                        ascore = assigned_value[index]
                        ascoreName = alart_name[ascore-1]
                    else:
                        ascore = 1
                        ascoreName = 'Low'

                    items.append(self.__buildNotification(
                        key.upper(), valueToCheckPii, index, values["data"][index], ascore, ascoreName))

        # If the method does not catch any PII, return an empty list
        if not items:
            return []

        total_alert_score = 0
        severityScores = ''
        for item in items:
            total_alert_score += item['Alert Score']
            if total_alert_score >= 4:
                severityScores = "EXTREME"
            elif total_alert_score == 3:
                severityScores = "HIGH"
            elif total_alert_score == 2:
                severityScores = "MEDIUM"
            else:
                severityScores = "LOW"

      # Get the current date

        current_date = datetime.datetime.now().date()
        return [{
            "job-type": "PRIVACY-VIOLATION",
            "modified-at": int(time.time()),
            "dataset": datasetID,
            "document ID": documentID,
            "documentTimestamp": processingTimestamp,
            "status": "ALERT",
            "severityScores": severityScores,
            "description": 'Personally identifiable information was detected in this document',
            'Fields': items
        }]
