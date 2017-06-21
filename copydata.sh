#!/bin/sh
DATE=`date +%Y%m%d` && mkdir -p ~/emg_data/ipa_emg/$1_$DATE && cp ./data/* ~/emg_data/ipa_emg/$1_$DATE && rm -r ./data/*
