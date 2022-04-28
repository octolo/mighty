transaction = (
    "name",
    "backend",
    "trans_backend_id",
    "status",
)

document = (
    "transaction",
    "content_type",
    "object_id",
    "doc_backend_id",
    "status",
    "nb_signatories",
    "nb_locations",
    "is_proof",
    "hash_doc",
)

signatory = (
    "email",
    "phone",
    "fullname",
    "first_name",
    "last_name",
    "denomination",
    "transaction",
    "signatory",
    "sign_backend_id",
    "status",
    "mode",
    "color",
)

location = (
    "transaction",
    "signatory",
    "document",
    "loc_backend_id",
    "x",
    "y",
    "yb",
    "width",
    "height",
    "page",
)
