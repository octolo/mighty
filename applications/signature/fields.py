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
)

document = (
    "transaction",
    "content_type",
    "object_id",
    "backend_id",
    "status",
    "location",
    "to_sign",
)

document_sz = (
    "uid",
    "transaction",
    "status",
    "location",
    "to_sign",
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
    "location",
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
    "location",
    "color",
    "has_email",
    "has_phone",
)