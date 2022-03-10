import datetime

class PMValid:
    @property
    def is_valid_date(self):
        if not self.date_valid: 
            return False
        date_valid = datetime.datetime.strptime(self.date_valid, "%Y-%m-%d").date()
        return False if date_valid < datetime.date.today() else True

    @property
    def is_valid(self):
        try:
            self.check_validity()
        except ValidationError:
            return False
        return True

    def check_validity(self):
        if self.form_method == "IBAN":
            self.is_valid_iban
        else:
            self.is_valid_cb
