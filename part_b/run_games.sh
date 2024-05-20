#!/bin/bash

output_file="testing/habp-vs-greedyactions.txt"

for i in $(seq 1 100)
do
    echo "GAME ${i}: $(python3 -m referee -s 250 -t 180 habp_agent greedy_legal_actions_agent -v 0)" | tee -a "$output_file"
done