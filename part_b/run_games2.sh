#!/bin/bash

output_file="_testing_output/habp-vs-greedytoken.txt"

for i in $(seq 1 100)
do
    echo "GAME ${i}: $(python3 -m referee -s 250 -t 180 agentAB greedy_token_agent -v 0)" | tee -a "$output_file"
done