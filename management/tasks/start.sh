#!/bin/bash

PIDS=()
COLORS='
// {print "\033[37m" $0 "\033[39m"}
/(WARN|WARNING)/ {print "\033[1;33m" $0 "\033[0m"}
/(ERROR|CRIT)/ {print "\033[1;31m" $0 "\033[0m"}
'

HTEXT="usage:\n
\t() default value\n
\n
\tstart.sh -d (./manage.py) -c (celery) -r (redis-server) -v (npm) -t (templates/frontend)\n
\t         -l (log dir) -i (reset log)\n
\t         -h (show help)\n
"

usage()
{
    echo -e $HTEXT
}

VUETPL="frontend"
LOGDIR="logs"
FULLSERVICE=false
REDIS_CMD="redis-server"
DJANGO_CMD="./manage.py"
VUE_CMD="npm"
CELERY_CMD="celery"
NGROK_CMD="./ngrok http 8000"

# If multiple env with DEV_PORT, set different DJANGO_PORT per env"
if [[ -z "${DEV_PORT}" ]]; then
    DJANGO_PORT="8000"
else
    case $DEV_PORT in
        "8081")
            DJANGO_PORT="8001"
            ;;
        "8082")
            DJANGO_PORT="8002"
            ;;
        "8083")
            DJANGO_PORT="8003"
            ;;
    esac
fi

while true; do
    case $1 in
        -a)
            shift
            READLOG=1
            ;;
        -l)
            shift
            if [ ! -z $1 ] && [[ $1 != -* ]]; then
                LOGDIR=$1
            fi
            ;;
        -i)
            shift
            INIT=1
            ;;
        -d)
            DJANGO=1
            shift
            if [ ! -z $1 ] && [[ $1 != -* ]]; then
                DJANGO=$1
            fi
            ;;
        -v)
            VUE=1
            shift
            if [ ! -z $1 ] && [[ $1 != -* ]]; then
                VUE=$1
            fi
            ;;
        -t)
            shift
            if [ ! -z $1 ] && [[ $1 != -* ]]; then
                VUETPL=$1
            fi
            ;;
        -c)
            CELERY=1
            shift
            if [ ! -z $1 ] && [[ $1 != -* ]]; then
                CELERY=$1
            fi
            ;;
        -r)
            REDIS=1
            shift
            if [ ! -z $1 ] && [[ $1 != -* ]]; then
                REDIS=$1
            fi
            ;;
        -n)
            NGROK=1
            shift
            if [ ! -z $1 ] && [[ $1 != -* ]]; then
                NGROK=$1
            fi
            ;;
        -f)
            shift
            FULLSERVICE=true
            ;;
        -h)
            shift
            usage
            ;;
        -*) echo "$0: Unrecognized option $1" >&2
            exit 2;;
        *) break ;;
    esac
done


prep_term()
{
    LOGFILE=$LOGDIR/$2.log
    if [ $INIT ]; then
        `rm -f $LOGFILE`
    fi
    $1 >> $LOGFILE &
    PID=$!
    PIDS+=($!)
    echo "SERVICE: $1"
    echo "--PID: $!"
    echo "--LOG: $LOGFILE"
    echo ""
}

handle_term()
{
    for pid in "${PIDS[@]}"; do
        if [ "${pid}" ]; then
            kill -TERM "${pid}" 2>/dev/null
        else
            term_kill_needed="yes"
        fi
    done
}

wait_term()
{
    term_child_pid=$1
    if [ "${term_kill_needed}" ]; then
        kill -TERM "${term_child_pid}" 2>/dev/null
    fi
    wait ${term_child_pid} 2>/dev/null
    trap - TERM INT
    wait ${term_child_pid} 2>/dev/null
    echo "TERM: pid($term_child_pid)"
}

trap 'handle_term' TERM INT

if [ ! -d "/path/to/dir" ]; then
    `mkdir -p ${LOGDIR}`
fi

if [ ! -z ${REDIS+x} ] || [ $FULLSERVICE = true ]; then
    if [[ $REDIS == 1 ]]; then
        REDIS_CMD="redis-server"
    fi
    prep_term "${REDIS_CMD} --save '' --appendonly no" "redis"
fi

if [ ! -z ${CELERY+x} ] || [ $FULLSERVICE = true ]; then
    if [[ $CELERY == 1 ]]; then
        CELERY_CMD="celery"
    fi
    prep_term "${CELERY_CMD} -A configuration worker --loglevel=debug  --max-tasks-per-child 50 -f ${LOGDIR}/celery.log" "celery"
fi

if [ ! -z ${NGROK+x} ] || [ $FULLSERVICE = true ]; then
    if [[ $NGROK == 1 ]]; then
        NGROK_CMD="./ngrok"
    fi
    prep_term "${NGROK_CMD} http 8000" "ngrok"
fi

if [ ! -z ${DJANGO+x} ] || [ $FULLSERVICE = true ]; then
    if [[ $DJANGO == 1 ]]; then
        DJANGO_CMD="./manage.py"
    fi
    prep_term "${DJANGO_CMD} runserver 0.0.0.0:$DJANGO_PORT -v3" "django"
fi


if [ ! -z ${VUE+x} ] || [ $FULLSERVICE = true ]; then
    if [[ $VUE == 1 ]]; then
        VUE_CMD="npm"
    fi
    #export NODE_OPTIONS=--openssl-legacy-provider
    prep_term "${VUE_CMD} run serve --prefix ${VUETPL}" "vuejs"
fi

if [ ! ${#PIDS[@]} -eq 0 ]; then
    echo "Use: 'tail -f ${LOGDIR}/*.log | awk \"\$COLORS\"' to show log"
fi

if [ $READLOG ]; then
    tail -f ${LOGDIR}/*.log | awk "$COLORS"
fi

for pid in "${PIDS[@]}"; do
    wait_term $pid
done
