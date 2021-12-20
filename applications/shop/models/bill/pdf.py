
from mighty.applications.document import generate_pdf

class PDFModel:
    @property
    def bill_pdf_url(self):
        return self.get_url('pdf', arguments=self.url_args)

    @property
    def bill_pdf_context(self):
        return {
            "group_or_user": self.group_or_user, 
            "offer": self.offer, 
            "subscription": self.subscription, 
            "bill": self.bill,
        }

    @property
    def bill_pdf_name(self):
        return get_valid_filename("%s_%s.pdf" % (self.group_or_user, self.offer))

    @property
    def bill_pdf_content(self):
        return ShopConfig.invoice_template

    @property
    def bill_pdf_data(self):
        return {
            "file_name": self.bill_pdf_name,
            "context": self.bill_pdf_context,
            "content": self.bill_pdf_content,
        }

    @property
    def bill_to_pdf(self):
        pdf_data = self.bill_pdf_data
        final_pdf, tmp_pdf = generate_pdf(**pdf_data)
        tmp_pdf.close()
        return final_pdf
       