transaction = (
    "name",
    "backend",
    "backend_id",
    "status",
)

transaction_sz = (
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
    "transaction",
    "status",
    "location",
    "to_sign",
)

signatory = (
    "transaction",
    "signatory",
    "backend_id",
    "status",
    "role",
    "location",
    "color",
)

signatory_sz = (
    "transaction",
    "signatory",
    "status",
    "role",
    "location",
    "color",
)