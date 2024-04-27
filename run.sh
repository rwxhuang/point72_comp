#!/bin/bash

ctrl_c() {
    echo "Ctrl+C received. Terminating both processes..."
    # Terminate both Python scripts by sending SIGINT
    kill -SIGINT $pid1 $pid2
    exit 1
}

# Trap Ctrl+C and call the ctrl_c function
trap ctrl_c SIGINT

# Run the first Python script (web app) in the background
python3 -m streamlit run MainPage.py &

pid1=$!

# Run the second Python script (infinite poller) in the background
python3 poll.py &

pid2=$!

# Wait for both processes to finish
wait $pid1 $pid2

echo "Done."