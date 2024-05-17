# https://www.maileva.com/developpeur
# https://secure2.recette.maileva.com/

from django.core.files import File
from django.shortcuts import get_object_or_404
from django.template import Template
from mighty.applications.messenger.backends import MissiveBackend
from mighty.applications.messenger import choices as _c
from mighty.apps import MightyConfig
from mighty.functions import setting
from mighty.models import Missive
from mighty.functions import get_logger
from uuid import uuid4
import os, requests, json
logger = get_logger()

class Maileva(MissiveBackend):
    status_ref = {
        "PENDING": _c.STATUS_PENDING,
        "ACCEPTED": _c.STATUS_ACCEPTED,
        "PROCESSED": _c.STATUS_PROCESSED,
        "DRAFT": _c.STATUS_ERROR,
        "REJECTED": _c.STATUS_REJECTED,
        "PROCESSED_WITH_ERRORS": _c.STATUS_PROCESSED,
    }
    events = [
        "ON_STATUS_ACCEPTED",
        "ON_STATUS_REJECTED",
        "ON_STATUS_PROCESSED",
        "ON_DEPOSIT_PROOF_RECEIVED",
    ]
    fields = ["denomination", "fullname", "complement", "address"]
    user_cache = None
    sending_id = None
    access_token = None
    priority = 1
    header_offset = 72
    js_admin = False
    page = 0
    _logger = logger

    # PRICE
    color_first_c4 = setting("MAILEVA_COLOR_FIRST_C4", 0.73)
    color_next_c4 = setting("MAILEVA_COLOR_NEXT_C4", 0.48)
    nb_first_c4 = setting("MAILEVA_NB_FIRST_C4", 0.48)
    nb_next_c4 = setting("MAILEVA_NB_NEXT_C4", 0.23)
    archiving_lte3_first = setting("MAILEVA_ARCHIVING_LTE3_FIRST", 0.03)
    archiving_lte6_first = setting("MAILEVA_ARCHIVING_LTE6_FIRST", 0.03)
    archiving_lte10_first = setting("MAILEVA_ARCHIVING_LTE10_FIRST", 0.03)
    archiving_lte3_next = setting("MAILEVA_ARCHIVING_LTE3_NEXT", 0.03)
    archiving_lte6_next = setting("MAILEVA_ARCHIVING_LTE6_NEXT", 0.03)
    archiving_lte10_next = setting("MAILEVA_ARCHIVING_LTE10_NEXT", 0.03)

    # CONFIG
    color_printing = setting("MAILEVA_COLOR_PRINTING", False)
    duplex_printing = setting("MAILEVA_DUPLEX_PRINTING", True)
    optional_address_sheet = setting("MAILEVA_OPTIONAL_ADDRESS_SHEET", True)
    archiving_duration = setting("MAILEVA_ARCHIVING_DURATION", 3)
    notification_email = setting("MAILEVA_NOTIFICATION", False)

    # SENDER
    sender_address_line_1 = setting("MAILEVA_SENDER1")
    sender_address_line_2 = setting("MAILEVA_SENDER2")
    sender_address_line_3 = setting("MAILEVA_SENDER3")
    sender_address_line_4 = setting("MAILEVA_SENDER4")
    sender_address_line_5 = setting("MAILEVA_SENDER5")
    sender_address_line_6 = setting("MAILEVA_SENDER6")
    sender_country_code = setting("MAILEVA_SENDERC")


    def __init__(self, missive, *args, **kwargs):
        super().__init__(missive, *args, **kwargs)
        self.color_first_c4 = kwargs.get("color_first_c4", self.color_first_c4)
        self.color_next_c4 = kwargs.get("color_next_c4", self.color_next_c4)
        self.nb_first_c4 = kwargs.get("nb_first_c4", self.nb_first_c4)
        self.nb_next_c4 = kwargs.get("nb_next_c4", self.nb_next_c4)
        self.archiving_lte3_first = kwargs.get("archiving_lte3_first", self.archiving_lte3_first)
        self.archiving_lte6_first = kwargs.get("archiving_lte6_first", self.archiving_lte6_first)
        self.archiving_lte10_first = kwargs.get("archiving_lte10_first", self.archiving_lte10_first)
        self.archiving_lte3_next = kwargs.get("archiving_lte3_next", self.archiving_lte3_next)
        self.archiving_lte6_next = kwargs.get("archiving_lte6_next", self.archiving_lte6_next)
        self.archiving_lte10_next = kwargs.get("archiving_lte10_next", self.archiving_lte10_next)
        self.color_printing = kwargs.get("color_printing", self.color_printing)
        self.duplex_printing = kwargs.get("duplex_printing", self.duplex_printing)
        self.optional_address_sheet = kwargs.get("optional_address_sheet", self.optional_address_sheet)
        self.archiving_duration = kwargs.get("archiving_duration", self.archiving_duration)
        self.notification_email = kwargs.get("notification_email", self.notification_email)
        self.sender_address_line_1 = kwargs.get("sender_address_line_1", self.sender_address_line_1)
        self.sender_address_line_2 = kwargs.get("sender_address_line_2", self.sender_address_line_2)
        self.sender_address_line_3 = kwargs.get("sender_address_line_3", self.sender_address_line_3)
        self.sender_address_line_4 = kwargs.get("sender_address_line_4", self.sender_address_line_4)
        self.sender_address_line_5 = kwargs.get("sender_address_line_5", self.sender_address_line_5)
        self.sender_address_line_6 = kwargs.get("sender_address_line_6", self.sender_address_line_6)
        self.sender_country_code = kwargs.get("sender_country_code", self.sender_country_code)

    @property
    def sender_height(self):
        return 145-self.header_offset

    @property
    def address_block(self):
        sender_style = "height:%spx;" % (str(self.sender_height))
        target_style = "height:171px;padding-bottom:35px;"
        sender_content = ""
        target_content = ""
        if self.missive.status == _c.STATUS_FILETEST:
            sender_style += "background-color:gray;color: white;"
            target_style += "background-color:blue;color: white;"
            sender_content = "SENDER"
            target_content = "TARGET"
        return """<div style="%s">%s</div><div style="%s">%s</div>""" % (sender_style, sender_content, target_style, target_content)

    def postal_template(self, context):
        return Template(self.address_block+self.missive.html).render(context)

    @property
    def auth_data(self):
        return {
            "username": setting("MAILEVA_USERNAME"),
            "password": setting("MAILEVA_PASSWORD"),
            "grant_type": "password",
            "client_id": setting("MAILEVA_CLIENTID"),
            "client_secret": setting("MAILEVA_SECRET"),
        }

    @property
    def postal_data(self):
        base = {
            "name": self.missive.target,
            "custom_id": self.missive.msg_id,
            "custom_data": self.missive.msg_id,
            "color_printing": self.color_printing,
            "duplex_printing": self.duplex_printing,
            "optional_address_sheet": self.optional_address_sheet,
            #"notification_email": self.notification_email,
            "archiving_duration": self.archiving_duration,
            "sender_address_line_1": self.sender_address_line_1,
            "sender_address_line_2": self.sender_address_line_2,
            "sender_address_line_3": self.sender_address_line_3,
            "sender_address_line_4": self.sender_address_line_4,
            "sender_address_line_5": self.sender_address_line_5,
            "sender_address_line_6": self.sender_address_line_6,
            "sender_country_code": self.sender_country_code,
        }
        if self.missive.model == _c.MODE_POSTALAR:
            base.update({
                "acknowledgement_of_receipt": True,
                "acknowledgement_of_receipt_scanning": False,
            })
        return base

    @property
    def user_webhook(self):
        if not self.user_cache:
            from oauth2_provider.models import Application
            self.user_cache = Application.objects.get(user__email=setting("MAILEVA_OAUTH_EMAIL"))
        return self.user_cache

    @property
    def webhook_data(self):
        return {
            "resource_type": self.resource_type,
            "callback_url": self.callback_url,
            #"authentication": {
            #    "oauth2": {
            #        "oauth2_server": MightyConfig.webhook + "/oauth2/token/",
            #        "client_id": self.user_webhook.client_id,
            #        "client_secret": setting("MAILEVA_OAUTH_SECRET"),
            #        "grant_type": "client_credentials"
            #    }
            #}
        }

    @property
    def target_data(self):
        data = {
            "custom_id":  self.missive.msg_id,
            "custom_data": self.missive.msg_id,
            "address_line_6": self.missive.city,
            "address_line_5": self.missive.cedex or self.missive.cedex_code or self.missive.special or "",
            "country_code": self.missive.country_code.upper(),
        }
        for i, field in enumerate(self.fields):
            attr = getattr(self.missive, field)
            if attr:
                data["address_line_"+str(i+1)] = attr[:38]
        return data

    @property
    def api_url(self):
        if setting('ENV', False) != "PRODUCTION":
            return self.api_sandbox
        return self.api_official

    @property
    def api_headers(self):
        return {
            'accept': 'application/json',
            'Authorization': 'Bearer '+self.access_token,
        }

    def valid_response(self, response):
        if response.status_code not in [200, 201]:
            self.missive.trace = str(response.content)
            if str(response.status_code).startswith("4"):
                if "code" in response.json():
                    self.missive.code_error = response.json()["code"]
                else:
                    self.missive.code_error = response.json()["error"]
            self.in_error = True
            return False
        return True

    def authentication(self):
        response = requests.post(self.api_url["auth"], data=self.auth_data)
        if self.valid_response(response):
            self.access_token = response.json()["access_token"]
            return True
        return False

    def create_sending(self):
        response = requests.post(self.api_url["sendings"], headers=self.api_headers, json=self.postal_data)
        self.sending_id = response.json()["id"]
        self.missive.partner_id = self.sending_id
        return self.valid_response(response)

    def check_documents(self):
        if self.authentication():
            url = self.api_url["documents"] % self.missive.partner_id
            response = requests.get(url, headers=self.api_headers)
            rjson = response.json()
            return rjson

    def postal_add_attachment(self, attachment):
        self.priority+=1
        api = self.api_url["documents"] % self.sending_id
        headers = self.api_headers
        doc_name = os.path.basename(attachment.name)
        files = {'document': (doc_name, attachment)}
        data = {'metadata': json.dumps({"priority": self.priority, "name": doc_name})}
        response = requests.post(api, headers=headers, files=files, data=data)
        self.valid_response(response)
        self.add_log_array("attachments", doc_name)

    def postal_attachments(self):
        if self.missive.attachments:
            for document in self.missive.attachments:
                self.postal_add_attachment(document)
        return False if self.in_error else True

    def add_recipients(self):
        api = self.api_url["recipients"] % self.sending_id
        response = requests.post(api, headers=self.api_headers, json=self.target_data)
        return self.valid_response(response)

    def submit(self):
        api = self.api_url["submit"] % self.sending_id
        response = requests.post(api, headers=self.api_headers)
        return self.valid_response(response)

    def enable_webhooks(self):
        for event in self.events:
            wdata = self.webhook_data
            wdata["event_type"] = event
            api = self.api_url["webhook"]
            response = requests.post(api, headers=self.api_headers, json=wdata)
            self.valid_response(response)

    def on_webhook(self, request):
        key = request.GET.get("key")
        if key:
            missive = get_object_or_404(Missive, msg_id=key)
        else:
            partner_id = request.POST.get("resource_id")
            missive = get_object_or_404(Missive, partner_id=partner_id)
        missive.check_status()

    def send_postal(self):
        #self.set_price_config()
        self.missive.msg_id = str(uuid4())
        if self.missive.status == _c.STATUS_FILETEST:
            self.postal_base()
        elif self.authentication():
            if not self.in_error:
                self.create_sending()
            if not self.in_error:
                self.add_recipients()
            if not self.in_error:
                self.postal_base()
                self.postal_attachments()
            if not self.in_error and self.submit():
                self.missive.to_sent()
                #self.set_price_info()
                if setting("MAILEVA_WEBHOOK"):
                    self.enable_webhooks()
            else:
                self.missive.to_error()
            getattr(self, "check_%s" % self.missive.mode.lower())()
            return self.missive.status

    def price_archive(self, page, archive):
        if not archive or not page:
            return 0
        elif archive <= 3:
            return self.archiving_lte3_first+(self.archiving_lte3_next*(page-1))
        elif archive <= 6:
            return self.archiving_lte6_first+(self.archiving_lte6_next*(page-1))
        elif archive <= 10:
            return self.archiving_lte10_first+(self.archiving_lte10_next*(page-1))

    def price_page(self, count_page, color=False, archive=0):
        price, pnext, parchive = (0.73, 0.48) if color else (0.48, 0.23)
        if count_page > 1: price += (pnext*(count_page-1))
        price += self.price_archive(count_page, archive)
        return price

    def price_config(self):
        return {
            "color_first_c4": self.color_first_c4,
            "color_next_c4": self.color_next_c4,
            "nb_first_c4": self.nb_first_c4,
            "nb_next_c4": self.nb_next_c4,
            "archiving_lte3_first": self.archiving_lte3_first,
            "archiving_lte6_first": self.archiving_lte6_first,
            "archiving_lte10_first": self.archiving_lte10_first,
            "archiving_lte3_next": self.archiving_lte3_next,
            "archiving_lte6_next": self.archiving_lte6_next,
            "archiving_lte10_next": self.archiving_lte10_next,
        }

    def prince_info(self):
        return {
            "count_page": self.count_page,
            "duplex_printing": self.duplex_printing,
            "color_printing": self.color_printing,
            "archiving_duration": self.archiving_duration,
            "optional_address_sheet": self.optional_address_sheet
        }

    def price(self):
        pages = self.price_info["count_page"]
        pages += 1 if self.prince_info["optional_address_sheet"] else 0
        price_page = self.price_page(
            count_page=pages,
            color=self.price_info["color_printing"],
            archive=self.prince_info["archiving_duration"]
        )
