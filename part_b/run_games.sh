#!/bin/bash

output_file="_testing_final/habp-vs-greedy.txt"

for i in $(seq 1 100)
do
    echo "GAME ${i}: $(python3 -m referee -s 250 -t 180 agent agentGreedy -v 0)" | tee -a "$output_file"
done