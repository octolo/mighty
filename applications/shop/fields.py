service = (
    'name',
    'code',
)
offer = (
    'named_id',
    'name',
    'frequency',
    'duration',
    'price',
    'service',
    'is_custom',
)
subscription = (
    'group',
    'offer',
    'bill',
    'discount',
    'next_paid',
    'date_start',
    'date_end',
)
bill = (
    'group',
    'amount',
    'date_payment',
    'paid',
    'payment_id',
    'subscription',
    'method',
)
discount = (
    'code',
    'amount',
    'is_percent',
    'date_end',
)
payment_method = (
    'group',
    'form_method',
    'iban',
    'bic',
    'cb',
    'date_cb',
    'backend',
    'service_id',
    'service_detail',
)
subscription_group = (
    'last_subscription',
    'valid_method',
    'one_use_count',
)