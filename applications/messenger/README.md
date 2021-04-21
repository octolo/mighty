# main.cf
transport_maps = hash:/etc/postfix/transport.maps
notify_classes = bounce,delay,data,policy,protocol,resource,software
max_idle = 10s
maximal_backoff_time = 10s
bounce_queue_lifetime = 1m
maximal_queue_lifetime = 1m
bounce_notice_recipient = {{ USER DJANGO }}
delay_notice_recipient = {{ USER DJANGO }}
error_notice_recipient = {{ USER DJANGO }}

# transport.maps
gyn@ArchlinuxVM01.localdomain   handle_status:
# postmap transport.maps

# master.cf
handle_status unix - n n - - pipe
    flags=FRq user=gyn argv={{ PATH_DJANGO }}/mighty/applications/messenger/management/handleStatusMail.sh {{ PATH_PYTHON_ENV }} {{ PATH_MANAGE_PY }}
