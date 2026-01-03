#!/bin/bash

# Bakery Analysis Pipeline
# Runs all analysis scripts in sequence

set -e  # Exit on any error

echo "Starting bakery analysis pipeline..."
echo "===================================="
echo

for script in 0*.py; do
    echo "Running $script..."
    python3 "$script"
    echo "✓ Completed $script"
    echo
done

echo "===================================="
echo "Pipeline completed successfully!"
