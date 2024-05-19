#!/bin/bash

output_file="testing/negamax-vs-random.txt"

for i in $(seq 1 100)
do
    echo "GAME ${i}: $(python3 -m referee -s 250 -t 180 habp_agent random_agent -v 0)" | tee -a "$output_file"
done