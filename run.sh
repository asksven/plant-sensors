#!/bin/bash
source setenv
mkdir -p logs
python poller.py >> logs/plant-sensors_`date "+%Y-%m-%d_%H%M"`
find logs -name "plant-sensors_*" -type f -mtime +30 -delete 
