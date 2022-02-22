from mighty.applications.signature.backends import SignatureBackend
from mighty.applications.signature import choices as _c
from mighty.functions import setting
import os, requests, json
from requests.auth import HTTPBasicAuth

class SignatureBackend(SignatureBackend):
    APIKEY = setting('DOCAGE_KEY', '86002628-1a83-434c-ba1e-72731a8b5318')
    APIUSER = setting('DOCAGE_USER', 'louis@easyshares.io')
    STATUS_TRANSACTION = {
        "Draft": _c.PREPARATION,
        "Scheduled": _c.READY,
        "WaitingInformations": _c.WAITING,
        "Active": _c.WAITING,
        "Validated": _c.WAITING,
        "Signed": _c.SIGNED,
        "Expired": _c.ERROR,
        "Refused": _c.REFUSED,
        "Aborted": _c.CANCELLED,
    }

    location_order = ["x", "yb", "width", "height"]
    api_url = {
        # Transaction
        'create_transaction' : 'https://api.docage.com/Transactions',
        'status_transaction': 'https://api.docage.com/Transactions/Status/%s',
        'cancel_transaction': 'https://api.docage.com/Transactions/Abort/%s',
        'remind_transaction': 'https://api.docage.com/Transactions/SendReminders/%s',
        'start_transaction' : 'https://api.docage.com/Transactions/LaunchTransaction/%s',
        # Document
        'add_document' : 'https://api.docage.com/TransactionFiles',
        # Signatory
        'add_member' : 'https://api.docage.com/TransactionMembers',
        'add_contact': 'https://api.docage.com/Contacts',
        # Location
        'add_location' : 'https://api.docage.com/SignatureLocations',


        'entity' : 'https://api.docage.com/Contacts',
        'entity_with_id': 'https://api.docage.com/Contacts/%s',
        'batch_delete_entity' : 'https://api.docage.com/Contacts/BatchDelete',
        'stop_transaction' : 'https://api.docage.com/Transactions/Abort/%s',
        'launch' : 'https://api.docage.com/Transactions/LaunchTransaction/%s',
        'batch_delete_document' : 'https://api.docage.com/TransactionFiles/BatchDelete',
        'batch_delete_member' : 'https://api.docage.com/TransactionMembers/BatchDelete',
        'webhook' : 'https://api.docage.com/Webhooks',
        'webhook_endpoint' : 'https://webhook.site/96929467-6c3c-4cdf-910f-33d4f4a467f7',
    }

    def get_url(self, url, interpolates=None):
        url = self.api_url[url] % interpolates if interpolates else self.api_url[url]
        self.logger.info("Docage URL: %s" % url)
        return url

    @property
    def auth(self):
        return HTTPBasicAuth(self.APIUSER, self.APIKEY)

    @property
    def headers(self):
        return {'Content-Type': 'application/json'}

    def change_status(self, status):
        self.transaction.status = self.STATUS_TRANSACTION[status]

    def generate_post_request(self, url, data=None, *args, **kwargs):
        payload = {"auth": self.auth, "headers": self.headers}
        if data: payload["data"] = json.dumps(data)
        return requests.post(url, **payload, **kwargs)

    def generate_get_request(self, url, data=None):
        payload = {"auth": self.auth, "headers": self.headers}
        if data: payload["data"] = json.dumps(data)
        return requests.get(url, **payload)

    def files_post_request(self, url, data, files):
        return requests.post(
            url,
            auth=self.auth,
            data=data,
            files=files,
            timeout=30,
        )


    # Transaction
    def new_transaction(self):
        transaction = self.generate_post_request(
            self.get_url("create_transaction"), 
            {
                "Name": self.transaction.name,
                "IsTest": setting("DEBUG"),
            })
        transaction = json.loads(transaction.content)
        self.logger.info("ID: %s" % transaction)
        self.transaction.backend_id = transaction
        self.transaction.add_log("info", transaction, "create")

    def status_transaction(self):
        transaction = self.generate_get_request(self.get_url("status_transaction", self.transaction.backend_id))
        transaction = json.loads(transaction.content)
        self.logger.info("Status: %s" % transaction)
        self.transaction.add_log("info", transaction, "status")
        self.change_status(transaction)

    def create_transaction(self):
        if not self.transaction.backend_id:
            self.new_transaction()
        else:
            self.status_transaction()
        self.transaction.save()

    def cancel_transaction(self):
        transaction = self.generate_get_request(self.get_url("cancel_transaction", self.transaction.backend_id))
        transaction = json.loads(transaction.content)
        self.transaction.add_log("info", transaction, "cancel")

    def remind_transaction(self):
        transaction = self.generate_get_request(self.get_url("remind_transaction", self.transaction.backend_id))
        transaction = json.loads(transaction.content)
        self.transaction.add_log("info", transaction, "remind")
    
    def start_transaction(self):
        transaction = self.generate_post_request(self.get_url("start_transaction", self.transaction.backend_id))
        self.status_transaction()
        self.transaction.save()
    

    # Documents
    def document_type(self, document):
        return 0 if document.to_sign else 1

    def create_document(self, document):
        document_file = document.file_to_use
        data = {
            'TransactionId': self.transaction.backend_id,
            'FileName': os.path.basename(document_file.name),
            'FriendlyName': document.name,
            'Type': self.document_type(document)
        }
        files = [('FileToUpload',('file',document_file.read(), 'application/octet-stream'))]
        response = self.files_post_request(self.get_url("add_document"), data, files)
        response = json.loads(response.content)
        document.add_log("info", response, "create")
        document.backend_id = response
        document.save()
        return response

    def add_document(self, document):
        self.logger.info("Add doc: %s" % document.name)
        if not document.backend_id:
            return self.create_document(document)

    def add_all_documents(self):
        for doc in self.transaction.documents:
            self.add_document(doc)


    # Members
    def add_contact(self, member):
        data = {
            "Email": member.getattr_signatory("signatory_email", False),
            "FirstName": member.getattr_signatory("signatory_first_name", False),
            "LastName": member.getattr_signatory("signatory_last_name", False),
            "Mobile": member.getattr_signatory("signatory_phone", False),
            "Phone": member.getattr_signatory("signatory_phone", False),
        }
        response = self.generate_post_request(self.get_url("add_contact"), data)
        response = json.loads(response.content)
        signatory = member.signatory
        signatory.add_cache(self.path, response)
        signatory.save()
        return response

    def get_entity_id(self, member):
        entity_id = member.signatory.has_cache_field(self.path)
        return member.signatory.cache[self.path] if entity_id else self.add_contact(member)

    def member_role(self, member):
        return 0 if member.role == _c.SIGNATORY else 2

    def sign_mode(self, member):
        return 1 if member.mode == _c.EMAIL else 0

    def create_member(self, member):
        data = {
            "TransactionId": self.transaction.backend_id,
            "ContactId": self.get_entity_id(member),
            "FriendlyName": member.fullname,
            "MemberRole": self.member_role(member),
            "SignMode": self.sign_mode(member)
        }
        response = self.generate_post_request(self.get_url("add_member"), data)
        response = json.loads(response.content)
        member.add_log("info", response, "create")
        member.backend_id = response
        member.save()
        return response

    def add_signatory(self, signatory):
        self.logger.info("Add member: %s" % signatory.fullname)
        if not signatory.backend_id:
            return self.create_member(signatory)

    def add_all_signatories(self):
        for mbr in self.transaction.signatories:
            self.add_signatory(mbr)

    # Locations
    def create_location(self, location):
        data = {
            "TransactionMemberId": location.signatory.backend_id,
            "TransactionFileId": location.document.backend_id,
            "Coordinates": ','.join([str(getattr(location, f)) for f in self.location_order]),
            "Pages": location.page,
        }
        response = self.generate_post_request(self.get_url("add_location"), data)
        response = json.loads(response.content)
        location.add_log("info", response, "create")
        location.backend_id = response
        location.save()
        return response

    def add_location(self, location):
        self.logger.info("Add location: %s" % location.id)
        if not location.backend_id:
            return self.create_location(location)

    def add_all_locations(self):
        for loc in self.transaction.locations:
            self.add_location(loc)



    """ OLD """

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

    def launch_transaction(self, instance, data):
        print(instance)
        print(data)
        # self.prepare_launch()
        # url = self.api_url["launch"] % instance.transaction_id
        # response = requests.post(url, auth=HTTPBasicAuth(self.APIUSER, self.APIKEY), headers=self.api_headers, data={})
        # return response
        return

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
