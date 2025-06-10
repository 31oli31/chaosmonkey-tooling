#!/bin/bash

# WARNING: This script will attempt to fill the disk in the current directory.
# This is intended for chaos engineering tests.
# Run this script with caution.

TARGET_FILE="chaos_monkey_fill_disk.tmp"
echo "This script will create a large file called '$TARGET_FILE' to fill the disk."
echo "Press Ctrl+C to stop the script and clean up the file."

# Function to clean up the created file on exit
cleanup() {
    echo -e "\n\nScript interrupted. Deleting '$TARGET_FILE'..."
    rm -f "$TARGET_FILE"
    echo "Cleanup complete."
    exit 0
}

# Set up the trap to call the cleanup function on interrupt
trap cleanup INT

# Loop to write 1MB chunks until the disk is full
while true; do
    # Append 1MB of zeros to the target file, supressing dd's output
    dd if=/dev/zero bs=1048576 count=1 >> "$TARGET_FILE" 2>/dev/null
    # If dd fails, it's likely because the disk is full
    if [ $? -ne 0 ]; then
        echo -e "\nDisk is full or an error occurred. The large file is '$TARGET_FILE'."
        # Exit without cleaning up so the disk remains full for testing
        trap - INT # remove the trap so we don't clean up
        exit 1
    fi
    # Provide some feedback to the user that the script is running
    echo -n "."
done 