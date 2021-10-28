from mighty.applications.signature.backends import SignatureBackend
from mighty.functions import setting

import os, requests, json
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)

class SignatureBackend(SignatureBackend):
    APIKEY = setting('DOCAGE_KEY', '86002628-1a83-434c-ba1e-72731a8b5318')
    APIUSER = setting('DOCAGE_USER', 'louis@easyshares.io')

    api_url = {
        'entity' : 'https://api.docage.com/Contacts',
        'batch_delete_entity' : 'https://api.docage.com/Contacts/BatchDelete',
        'transaction' : 'https://api.docage.com/Transactions',
        'file' : 'https://api.docage.com/TransactionFiles',
        'member' : 'https://api.docage.com/TransactionMembers',
        'location' : 'https://api.docage.com/SignatureLocations',
        'launch' : 'https://api.docage.com/Transactions/LaunchTransaction/%s'
    }

    docage_dict = {
        'TO_SIGN': 0,
        'TO_ADD': 1,
        'BY_SMS': 0,
        'BY_EMAIL': 1,
        'SIGN': 0,
        'WATCH': 2,
    }

    @property
    def api_headers(self):
        return {
            'Content-Type': 'application/json'
        }

    def create_entity(self, instance):
        payload = {}
        to_entity = instance.contact
        if instance.contact.has_representative :
            to_entity = instance.contact.load_representatives().first()
        if to_entity.first_name and to_entity.last_name:
            payload['FirstName'] = to_entity.first_name
            payload['LastName'] = to_entity.last_name
            if to_entity.email_pref: payload['Email'] = to_entity.email_pref
            if to_entity.phone_pref: payload['Mobile'] = to_entity.phone_pref
            payload = json.dumps(payload)
            response = requests.post(self.api_url["entity"], auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
            return response
        return

    def create_transaction(self, instance):
        payload_dict = {
            "IsTest": "true"
        }
        if instance.transaction_name: payload_dict['Name'] = instance.transaction_name
        payload = json.dumps(payload_dict)
        response = requests.post(self.api_url["transaction"], auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        return response

    def add_file(self, instance):
        payload = {
            'TransactionId': instance.transaction.transaction_id,
            'FileName': instance.document_name,
            'FriendlyName': instance.friendly_name,
            'Type': self.docage_dict[instance.document_type]
        }
        document = instance.document.document_file.last().file
        read_file = document.open('rb').read()
        files=[
            (instance.friendly_name,(document.name,read_file,'application/octet-stream'))
        ]
        response = requests.post(self.api_url["file"], auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload, files=files)
        print(response.raw.__dict__)
        return response

    def add_member(self, instance):
        payload = json.dumps({
            "TransactionId": instance.transaction.transaction_id,
            "ContactId": instance.entity.entity_id,
            "FriendlyName": instance.friendly_name,
            "MemberRole": self.docage_dict[instance.member_role],
            "SignMode": self.docage_dict[instance.sign_mode]
        })
        response = requests.post(self.api_url["member"], auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        return response

    def add_signature_location(self, instance):
        payload = json.dumps({
            "TransactionMemberId": instance.member.transaction_member_id,
            "TransactionFileId": instance.document.transaction_document_id,
            "Coordinates": instance.coordinates,
            "Pages": instance.page
        })
        response = requests.post(self.api_url["location"], auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        return response

    def launch_transaction(self, instance):
        url = self.api_url["launch"] % instance.transaction_id
        response = requests.post(url, headers=self.api_headers)
        return response