#!/bin/bash

/bin/ollama serve &

pid=$!

sleep 5

echo "Retrieving models"
ollama pull mxbai-embed-large
ollama pull llama3.2:3b
echo "Done!"

wait $pid
