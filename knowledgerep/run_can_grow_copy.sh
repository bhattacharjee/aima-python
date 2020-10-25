#!/usr/bin/env ksh

    CONFIG_NUM=$1
    name="config_${CONFIG_NUM}_can_grow"
    DIR="${PWD}/output/${name}"

    print $DIR
    mkdir -p $DIR

    echo f"./A1_COMP9016_Bhattacharjee_Rajbir_R00195734_copy.py -ssp -ng -nonc -config ${CONFIG_NUM}" > $DIR/details.txt
    for i in 1
    do
        OUTPUT1="${DIR}/time_${i}.txt"
        OUTPUT2="${DIR}/out_${i}.txt"
        (time -v -o $OUTPUT1 ./A1_COMP9016_Bhattacharjee_Rajbir_R00195734_copy.py -ssp -ng -nonc -config $CONFIG_NUM) 2>&1 > $OUTPUT2
    done
