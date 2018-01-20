#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

while getopts iug OPT
do
    case $OPT in
    i) OPT_INIT=1
        ;;
    u) OPT_UPDATE=1
        ;;
    g) OPT_GRAPH=1
        ;;
    esac
done

RRD=/home/naoaki/db.rrd

if [ $OPT_INIT ]; then
    rrdtool create ${RRD} \
        --start `date +%s` \
        --step 60 \
        DS:delay:GAUGE:120:0:5 \
        RRA:MIN:0.5:5:20 \
        RRA:MAX:0.5:5:20 \
        RRA:AVERAGE:0.5:5:20
fi

if [ $OPT_UPDATE ]; then
    DELAY=`curl -so /dev/null -w '%{time_total}\n' http://www.yahoo.co.jp/`
    rrdtool update ${RRD} `date +%s`:${DELAY}
    #rrdtool update ${RRD} `date +%s`:${DELAY}:${DELAY}:${DELAY}
fi

if [ $OPT_GRAPH ]; then
    rrdtool graph delay.png \
        --width 500 \
        --upper-limit 5.0 \
        --lower-limit 0 \
        --rigid \
        --imgformat PNG \
        DEF:delay_avg=${RRD}:delay:AVERAGE \
        DEF:delay_min=${RRD}:delay:MIN \
        DEF:delay_max=${RRD}:delay:MAX \
        LINE2:delay_avg#00FF00:"Avg" \
        LINE2:delay_min#FF0000:"Min" \
        LINE2:delay_max#0000FF:"Max"
fi

