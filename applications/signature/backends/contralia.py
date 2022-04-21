from mighty.applications.signature.backends import SignatureBackend
from mighty.functions import refn
from requests.auth import HTTPBasicAuth
import os, requests, json
import xml.etree.ElementTree as etree

class SignatureBackend(SignatureBackend):
    OFFER_CODE = "OCTOLOAPI-TEST"
    UNIQUE_CODE = "OCTOLOAPI-TEST-DISTRIB"
    APIUSER = "octoloapi-test"
    APIKEY = "WBgCTsRiBw6Pp!P"
    api_url = {
        # TRANSACTIONS
        "initiate": "/Contralia/api/v2/%s/transactions",
        "abort": "/Contralia/api/v2/transactions/%s/abort",
        "terminate": "/Contralia/api/v2/transactions/%s/terminate",
        "status": "/Contralia/api/v2/transactions/%s",
        # DOCUMENTS
        "upload": "/Contralia/api/v2/transactions/%s/document",
        "attachment": "/Contralia/api/v2/transactions/%s/attachment/%s",
        "remove": "/Contralia/api/v2/transactions/%s/removeDoc",
        # SIGNATORIES
        "signatory": "/Contralia/api/v2/transactions/%s/signatory/%s",
    }
    LEVEL = {
        "SIMPLE_LCP" : "pour les identiés Contralia",
        "ADVANCED_LCP" : "pour les identiés Contralia",
        "ADVANCED_NCP" : "pour les identiés Contralia",
        "ADVANCED_QCP" : "pour les identiés Contralia",
        "QUALIFIED" : "réservé pour les identiés Centralisées",
    }

    @property
    def DOMAIN(self):
        return "https://test.contralia.fr:443" if self.setting("DEBUG") else ""

    @property
    def auth(self):
        return HTTPBasicAuth(self.APIUSER, self.APIKEY)

    @property
    def headers(self):
        return {'Content-Type': 'application/x-www-form-urlencoded'}

    @property
    def customRef(self):
        return refn(self.transaction.id, self.transaction.uid, size=32)

    def requestRef(self, ref):
        return refn(ref, self.transaction.id, self.transaction.uid, size=32)

    def generate_delete_request(self, url, data=None, *args, **kwargs):
        payload = {"auth": self.auth, "headers": self.headers}
        if data: 
            payload["data"] = "&".join(["%s=%s" % (k, v) for  k,v in data.items()])
        r = requests.delete(url, **payload, **kwargs)
        self.logger.info(r.content)
        return r

    def generate_post_request(self, url, data=None, *args, **kwargs):
        payload = {"auth": self.auth, "headers": self.headers}
        if data: 
            payload["data"] = "&".join(["%s=%s" % (k, v) for  k,v in data.items()])
        r = requests.post(url, **payload, **kwargs)
        self.logger.info(r.content)
        return r

    def generate_get_request(self, url, data=None):
        payload = {"auth": self.auth, "headers": self.headers, "params": data}
        if "format" in data and data["format"] == "json":
            payload["headers"] = {'Content-Type': 'text/json'}
        r = requests.get(url, **payload)
        self.logger.info(r.content)
        return r

    def get_url(self, url, interpolates=None):
        url = self.DOMAIN + self.api_url[url] % interpolates if interpolates else self.api_url[url]
        self.logger.info("Contralia URL: %s" % url)
        return url

    # TRANSACTION
    def new_transaction(self):
        url = self.get_url("initiate", self.OFFER_CODE)
        data = {
            "offerCode": "OCTOLOAPI-TEST",
            "organizationalUnitCode": "OCTOLOAPI-TEST-DISTRIB",
            "customRef": self.customRef,
            "requestReference": self.requestRef("initiate"),
        }
        transaction = self.generate_post_request(url, data)
        transaction = etree.fromstring(transaction.content)
        self.logger.info("ID: %s" % transaction.get("id"))
        self.transaction.trans_backend_id = transaction.get("id")
        self.transaction.add_log("info", {"id": transaction.get("id")}, "create")

    def status_transaction(self):
        url = self.get_url("status", self.transaction.trans_backend_id)
        data = {
            "format": "json",
            "abortReason": "Octolo abort",
            "requestReference": self.requestRef("status"),
        }
        transaction = self.generate_get_request(url, data)
        transaction = json.loads(transaction.content)
        self.transaction.add_log("info", transaction, "status")
        self.transaction.save()

    def create_transaction(self):
        self.new_transaction() if not self.transaction.trans_backend_id else self.status_transaction()
        self.transaction.save()

    def cancel_transaction(self):
        if not self.transaction.is_immutable:
            url = self.get_url("abort", self.transaction.trans_backend_id)
            data = {
                "abortReason": "Octolo abort",
                "requestReference": self.requestRef("abort"),
            }
            transaction = self.generate_post_request(url, data)
            transaction = etree.fromstring(transaction.content)
            data = {
                "terminateDate": transaction.get("terminateDate"),
                "archivedVolume": transaction.get("archivedVolume"),
            }
            self.transaction.status = self._c.CANCELLED
            self.transaction.save()

    def end_transaction(self):
        if not self.transaction.is_immutable:
            url = self.get_url("terminate", self.transaction.trans_backend_id)
            data = { "requestReference": self.requestRef("terminate") }
            transaction = self.generate_post_request(url, data)
            transaction = etree.fromstring(transaction.content)
            data = {
                "terminateDate": transaction.get("terminateDate"),
                "archivedVolume": transaction.get("archivedVolume"),
            }
            self.transaction.add_log("info", data, "end")
            self.transaction.status = self._c.SIGNED
            self.transaction.save()
       
    # DOCUMENTS
    def files_post_request(self, url, data, files):
        r = requests.post(
            url,
            auth=self.auth,
            data=data,
            files=files,
            timeout=30,
        )
        self.logger.info(r.content)
        return r

    def add_document(self, document):
        self.logger.info("Add doc: %s" % document.name)
        if not document.doc_backend_id:
            return self.create_document(document)

    def add_all_documents(self):
        for doc in self.transaction.documents:
            self.add_document(doc)

    def add_sign_doc(self, document):
        document_file = document.file_to_use
        base_name = os.path.basename(document_file.name)
        data = {
            "name": document.name,
            "withoutProcessing": False,
            "archive": True,
            "signatureFormat": "PADES",
            "requestReference": self.requestRef(base_name),
        }
        files = {"file": document_file.read()}
        url = self.get_url("upload", self.transaction.trans_backend_id)
        return self.files_post_request(url, data, files)

    def add_annex_doc(self, document):
        document_file = document.file_to_use
        base_name = os.path.basename(document_file.name)
        data = {
            "description": document.name,
            "attachmentType": "ANNEX",
            "archive": True,
            "requestReference": self.requestRef(base_name),
        }
        files = {"file": document_file.read()}
        url = self.get_url("attachment", (self.transaction.trans_backend_id, document.uid))
        return self.files_post_request(url, data, files)

    def add_document(self, document):
        response = self.add_sign_doc(document) if document.to_sign else self.add_annex_doc(document)
        response = etree.fromstring(response.content)
        document.hash_doc = response.find("hash").text
        document.save()

    def remove_all_documents(self, document):
        for doc in self.transaction.documents:
            self.remove_document(doc)

    def remove_sign_doc(self, document):
        document_file = document.file_to_use
        url = self.get_url("remove", self.transaction.trans_backend_id)
        data = {
            "name": document.name,
            "requestReference": self.requestRef("docRmv"),
        }
        transaction = self.generate_post_request(url, data)
        transaction = etree.fromstring(transaction.content)
        self.transaction.save()

    def remove_annex_doc(self, document):
        document_file = document.file_to_use
        url = self.get_url("attachment", (self.transaction.trans_backend_id, document.uid))
        data = { "requestReference": self.requestRef("anxRmv") }
        transaction = self.generate_delete_request(url, data)
        transaction = etree.fromstring(transaction.content)
        self.transaction.save()

    def remove_document(self, document):
        response = self.remove_sign_doc(document) if document.to_sign else self.remove_annex_doc(document)

    # SIGNATORY
    def add_signatory(self, signatory):
        if signatory.need_to_sign:
            url = self.get_url("signatory", (self.transaction.trans_backend_id, signatory.id))
            data = {
                #"signatureLevel": "SIMPLE_LCP",
                "civility": 0 if signatory.getattr_signatory("is_man", False) else 1,
                "firstname": signatory.getattr_signatory("signatory_first_name", False),
                "lastname": signatory.getattr_signatory("signatory_last_name", False),
                "electronicSignature": True,
                "requestReference": self.requestRef(signatory.uid),
            }
            email = signatory.getattr_signatory("signatory_email", False)
            if email: data["email"] = email
            phone = signatory.getattr_signatory("signatory_phone", False)
            if phone: data["phone"] = phone
            response = self.generate_post_request(url, data)
            response = etree.fromstring(response.content)
            self.logger.info("ID: %s" % response.get("id"))
            signatory.sign_backend_id = response.get("id")
            signatory.add_log("info", {"id": response.get("id")}, "create")
            signatory.save()

    def add_all_signatories(self):
        for signatory in self.transaction.signatories:
            self.add_signatory(signatory)


    # LOCATION
    def add_location(self, location):
        raise NotImplementedError("Subclasses should implement add_location()")

    def add_all_locations(self):
        raise NotImplementedError("Subclasses should implement add_all_locations()")
