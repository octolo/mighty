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
        'entity_with_id': 'https://api.docage.com/Contacts/%s',
        'batch_delete_entity' : 'https://api.docage.com/Contacts/BatchDelete',
        'transaction' : 'https://api.docage.com/Transactions',
        'stop_transaction' : 'https://api.docage.com/Transactions/Abort/%s',
        'launch' : 'https://api.docage.com/Transactions/LaunchTransaction/%s',
        'document' : 'https://api.docage.com/TransactionFiles',
        'batch_delete_document' : 'https://api.docage.com/TransactionFiles/BatchDelete',
        'member' : 'https://api.docage.com/TransactionMembers',
        'batch_delete_member' : 'https://api.docage.com/TransactionMembers/BatchDelete',
        'location' : 'https://api.docage.com/SignatureLocations',
        'webhook' : 'https://api.docage.com/Webhooks',
        'webhook_endpoint' : 'https://webhook.site/96929467-6c3c-4cdf-910f-33d4f4a467f7',
    }

    docage_dict = {
        'TO_SIGN' : 0,
        'TO_ADD'  : 1,
        'BY_SMS'  : 0,
        'BY_EMAIL': 1,
        'SIGN'    : 0,
        'WATCH'   : 2,
    }

    @property
    def api_headers(self):
        return {
            'Content-Type': 'application/json'
        }

    def entity(self, instance, method=None):
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
            response = self.get_url_entity(instance, method, payload)
            return response
        return

    def get_url_entity(self, instance, method, payload):
        if method == "create":
            return requests.post(self.api_url["entity"] , auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        elif method == "update":
            return requests.put(self.api_url["entity_with_id"] % instance.entity_id , auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        elif method == "delete":
            return requests.delete(self.api_url["entity_with_id"] % instance.entity_id , auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers={}, data={})
        return requests.get(self.api_url["entity_with_id"] % instance.entity_id , auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers={}, data={})

    def transaction(self, instance):
        payload_dict = {
            "IsTest": "true"
        }
        if instance.transaction_name: payload_dict['Name'] = instance.transaction_name
        payload = json.dumps(payload_dict)
        response = requests.post(self.api_url["transaction"], auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        return response
    
    def annul_transaction(self, instance):
        url = self.api_url["stop_transaction"] % instance.transaction_id
        payload={}
        headers = {}
        response = requests.get(url, auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=headers, data=payload)
        return response

    def document(self, instance):
        import os
        document = instance.document
        document_file = document.document_file.last().file
        url = self.api_url["document"]

        payload = {
            'TransactionId': instance.transaction.transaction_id,
            'FileName': os.path.basename(document_file.name),
            'FriendlyName': document.name,
            'Type': self.docage_dict[instance.document_type]
        }
        files=[
            ('FileToUpload',('file',document_file.read(), 'application/octet-stream'))
        ]
        response = requests.request("POST", url,
            auth=HTTPBasicAuth(self.APIUSER, self.APIKEY),
            data=payload,
            files=files,
            timeout=30,
        )
        return response

    def delete_document(self, instance):
        payload = json.dumps([str(instance.transaction_document_id)])
        response = requests.delete(self.api_url["batch_delete_document"], auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        return response

    def member(self, instance):
        payload = json.dumps({
            "TransactionId": instance.transaction.transaction_id,
            "ContactId": instance.entity.entity_id,
            "FriendlyName": instance.friendly_name,
            "MemberRole": self.docage_dict[instance.member_role],
            "SignMode": self.docage_dict[instance.sign_mode]
        })
        response = requests.post(self.api_url["member"], auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        return response

    def delete_member(self, instance):
        payload = json.dumps([str(instance.transaction_member_id)])
        response = requests.delete(self.api_url["batch_delete_member"], auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        return response

    def signature_location(self, instance):
        coordinates = instance.coordinates.split(',')
        del coordinates[1]
        payload = json.dumps({
            "TransactionMemberId": instance.member.transaction_member_id,
            "TransactionFileId": instance.document.transaction_document_id,
            "Coordinates": ','.join(coordinates),
            "Pages": instance.page
        })
        response = requests.post(self.api_url["location"], auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        return response

    def launch_transaction(self, instance):
        url = self.api_url["launch"] % instance.transaction_id
        response = requests.post(url, auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data={})
        return response

    def create_webhook(self):
        url = self.api_url["webhook"]

        payload = json.dumps({
            "Url": self.api_url["webhook_endpoint"], #self.webhook_transaction_url
            "Name": "Transactions modifiées",
            "Description": "Modification des transactions",
            "EntityTypeName": "Transaction",
            "Action": "3",
            "TransactionStatusTarget": "-100"
        })

        response = requests.post(url, auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data=payload)
        return response
