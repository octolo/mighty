service = (
    "name",
    "key",
    "price",
    "has_counter",
)

offer = (
    "service",
    "name",
    "named_id",
    "frequency",
    "duration",
    "price",
    "is_custom",
)


subscription = (
    "group",
    "offer",
    "bill",
    "method",
    "discount",
    "next_paid",
    "date_start",
    "date_end",
    "coin",
    "is_used",
    "advance",
    "frequency",
    "status",
)

bill = (
    "group",
    "subscription",
    "service",
    "discount",
    "method",
    "date_paid",
    "date_payment",
    "paid",
    "numero",
    "status",
    "items",
    "backend",
    "payment_id",
    "action",
    "override_price",
    "amount",
    "end_discount",
    "end_amount",
    "tva_calc_month",
    "total_calc_month",
)

discount = (
    "code",
    "amount",
    "is_percent",
    "date_end",
)

payment_method = (
    "group",
    "owner",
    "form_method",
    "date_valid",
    "signature",
    "iban",
    "bic",
    "cb",
    "cvc",
    "month",
    "year",
    "backend",
    "service_id",
    "service_detail",
    "default",
    "need_to_valid_backend",
)

subscription_group = (
    'last_subscription',
    'valid_method',
    'one_use_count',
)