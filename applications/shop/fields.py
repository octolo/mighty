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
    'price_tenant',
    'service',
    'is_custom',
)
subscription = (
    'group',
    'offer',
    'status',
    'bill',
    'discount',
    'next_paid',
    'date_start',
    'date_end',
    'method',
)
bill = (
    'group',
    'status',
    'amount',
    'end_amount',
    'date_payment',
    'paid',
    'payment_id',
    'subscription',
    'method',
    'discount',
    'end_discount',
    'name',
    'items',
    'backend',
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
    'date_valid',
    'iban',
    'bic',
    'cb',
    'cvc',
    'month',
    'year',
    'backend',
    'service_id',
    'service_detail',
)
subscription_group = (
    'last_subscription',
    'valid_method',
    'one_use_count',
)