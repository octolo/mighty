discount = (
    'code',
    'amount',
    'is_percent',
    'date_end',
)

service = (
    'name',
    'key',
    'price',
    'tax',
    'number',
    'charge_at',
)

item = (
    'name',
    'key',
    'price',
    'tax',
    'number',
    'service',
)

offer = (
    'name',
    'named_id',
    'frequency',
    'duration',
    'is_custom',
    'price',
    'tax',
    'number',
    'service',
    'service_tenant',
    'need_quotation',
)


subscription = (
    'group',
    'offer',
    'bill',
    'method',
    'discount',
    'next_paid',
    'date_start',
    'date_end',
    'coin',
    'is_used',
    'advance',
    'frequency',
    'status',
)

bill = (
    'group',
    'subscription',
    'service',
    'discount',
    'method',
    'date_paid',
    'date_payment',
    'paid',
    'numero',
    'status',
    'items',
    'backend',
    'payment_id',
    'action',
    'override_price',
    'amount',
    'end_discount',
    'end_amount',
    'tva_calc_month',
    'total_calc_month',
)

payment_method = (
    'owner',
    'form_method',
    'date_valid',
    'signature',
    'iban',
    'bic',
    'cb',
    'cvc',
    'month',
    'year',
    'backend',
    'service_id',
    'service_detail',
    'default',
    'need_to_valid_backend',
    'status',
)

method = payment_method + (
    'group',
)

subscription_group = (
    'subscription',
    'valid_payment_methods',
    'valid_subscription',
)

subscription_request = payment_method + (
    'offer',
    'user',
    'frequency',
    'data',
)
