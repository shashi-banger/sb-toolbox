#!/bin/bash
for f in `ls -d ../../subtitle_data/subtitle_data/*`;
do
    xml_file=`basename ${f}`
    if [[ ! -e ./subtitle_data/$xml_file ]]
    then
        python get_key_words_and_subtitle.py --xml $f --out_xml_dir ./subtitle_data/ --out_sub_dir ./subtitle_data/subtitles/;
        sleep 2
    else
        echo $xml_file Exists
    fi
done
