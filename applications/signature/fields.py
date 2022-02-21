transaction = (
    "name",
    "backend",
    "backend_id",
    "status",
)

transaction_sz = (
    "uid",
    "name",
    "status",
    "has_signatory",
    "has_documents_to_sign",
    "has_contacts",
    "has_documents"
)

document = (
    "transaction",
    "content_type",
    "object_id",
    "backend_id",
    "status",
    "to_sign",
    "nb_signatories",
    "nb_locations",
)

document_sz = (
    "uid",
    "transaction",
    "status",
    "to_sign",
    "nb_signatories",
    "nb_locations",
    "name",
    "document_sign",
    "object_uid",
)

signatory = (
    "email",
    "phone",
    "transaction",
    "signatory",
    "backend_id",
    "status",
    "role",
    "mode",
    "color",
)

signatory_sz = (
    "uid",
    "email",
    "phone",
    "fullname",
    "picture",
    "transaction",
    "signatory",
    "status",
    "role",
    "mode",
    "color",
    "has_email",
    "has_phone",
)

location = (
    "transaction",
    "signatory",
    "document",
    "backend_id",
    "x",
    "y",
    "width",
    "height",
    "page",
)

location_sz = (
    "uid",
    "transaction",
    "signatory",
    "document",
    "x",
    "y",
    "width",
    "height",
    "page",
    "color",
    "fullname",
)