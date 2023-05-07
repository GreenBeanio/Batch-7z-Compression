#!/usr/bin/env python3
# region Import Modules
from pathlib import Path
import sys
import os
import subprocess
import shutil
import datetime
import pandas as pd
import numpy as np

# endregion Import Modules
# Path to save
save_path = ""
file_name = "compression_results"
# region code

# If the save path is empty use current working directory
if save_path == "":
    save_path = Path.cwd()
# Create the full output path
save_path = Path(save_path, f"{file_name}.csv")

# Data frame to hold stats
frame = pd.DataFrame(
    columns=[
        "Name",
        "Type",
        "Path",
        "Start",
        "End",
        "Elapsed",
        "Status",
        "Uncompressed",
        "Compressed",
        "Savings",
        "Ratio",
    ]
)


# If the user has failed you end yourself
def exit_compression(say):
    # If on windows run the cls command to clear the terminal
    if os.name == "nt":
        os.system("cls")
    # If on linux run the cls command to clear the terminal
    else:
        os.system("clear")
    # Send a message
    print(say)
    # Wait for input then close
    input()
    sys.exit()


# Check the amount of arguments
def check_arguments():
    if len(sys.argv) != 2:
        exit_compression(
            "Pass in 1 path to compress all files and directories inside of."
        )
    else:
        return "Passed"


# Check the argument to see if it's a valid directory
def check_for_path():
    if check_arguments() == "Passed":
        passed_path = Path(sys.argv[1])
        # Check if it's a valid path
        if passed_path:
            return passed_path
        else:
            exit_compression("Passed path isn't a valid directory.")


# Checks the sizes of a successful compression
def check_size(to_check):
    # Empty variables
    results = []
    # Searching for the results
    for line in to_check:
        split_line = line.split()
        # If the split_line is more than 2
        if len(split_line) >= 2:
            # If it is the uncompressed size
            if "Size:" in split_line[0]:
                results.append(int(split_line[1]))
            # If it is the compressed size (break because they'll be nothing worthwhile after)
            elif "Compressed:" in split_line[0]:
                results.append(int(split_line[1]))
                break
    return results


# Checks if the compression was successful
def check_success(standard_out):
    # Default Value is failed
    result = "Failed"
    # For each value
    for line in standard_out:
        # If the string is the subset it has passed
        if line == "Everything is Ok":
            result = "Passed"
            break
    # Return the value of if it passed or failed
    return result


# Deletes after compression
def delete(delete_type, delete_path):
    if delete_type == "File":
        os.remove(delete_path)
    elif delete_type == "Directory":
        shutil.rmtree(delete_path)


def write_entry(write_type):
    # Write to the file
    if write_type == "Write":
        frame.loc[0:].to_csv(
            save_path,
            sep=",",
            encoding="utf-8-sig",
            index=False,
            header=False,
            na_rep="N/A",
            mode="a",
        )
    # Create the file if it doesn't exist
    elif write_type == "Create":
        if os.path.isfile(save_path) == False:
            frame.to_csv(
                save_path,
                sep=",",
                encoding="utf-8-sig",
                index=False,
                header=True,
                na_rep="N/A",
                mode="w",
            )


# Compress the file
def compression(base_path, full_path, object_type):
    # Start time of the compression
    start_time = datetime.datetime.now()
    # Get the name for statistics
    name = full_path.name
    # Get the stem of the item to be encrypted
    stem = full_path.stem
    output_path = Path(base_path, f"{stem}.7z")
    # Run 7z to create an archive
    subprocess.run(
        ["7z", "a", f"{output_path}", f"{full_path}"],
        shell=False,
        capture_output=True,
        text=True,
    )
    # Test the archive!
    test_result = subprocess.run(
        ["7z", "t", f"{output_path}"],
        shell=False,
        capture_output=True,
        text=True,
    )
    # Variable to store results
    sizes = [0, 0]
    # List of all the lines from the result
    stdout = test_result.stdout.split("\n")
    # Check for the success of the test (Think I can safely limit the results down to this range)
    check_results = check_success(stdout[8:-4])
    # If the archive passed
    if check_results == "Passed":
        # Get the sizes (Think it'll always be there, but not entirely sure)
        sizes = check_size(stdout[-3:-1])
        # Delete the source file/directory
        delete(object_type, full_path)
        print("7z Successful")
    # If the archive failed
    elif check_results == "Failed":
        # Delete the failed .7z
        delete("File", output_path)
        print("7z Failed")

    # Get statistics!
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time

    # Modifying for printing
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S:%f")
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S:%f")
    elapsed_time = datetime.datetime.utcfromtimestamp(
        elapsed_time.total_seconds()
    ).strftime("%H:%M:%S:%f")

    # Savings
    savings = sizes[0] - sizes[1]
    ratio = sizes[1] / sizes[0]

    # Save Stats
    entry = np.array(
        [
            name,
            object_type,
            full_path,
            start_time,
            end_time,
            elapsed_time,
            check_results,
            sizes[0],
            sizes[1],
            savings,
            ratio,
        ]
    )
    # Add to the data frame
    frame.loc[0] = entry
    # Save to csv
    write_entry("Write")


# For every object in the directory
def begin_compression():
    # Create the csv for stat storage if it doesn't already exist
    write_entry("Create")
    # Get the directory
    designated_path = check_for_path()
    # Get the items in the directory
    items = os.listdir(designated_path)
    # For every item in the directory
    for entry in items:
        # Get the current items full path
        full_item = Path(designated_path, entry)
        # Check if the item is a directory or file
        if full_item.is_file():
            # Get the extension type
            extension = full_item.suffix
            # If the file isn't already a 7z then compress it
            if extension != ".7z":
                # Compress the file
                compression(designated_path, full_item, "File")
            else:
                print("7z Skipped")
        elif full_item.is_dir():
            # Compress the directory
            compression(designated_path, full_item, "Directory")


begin_compression()
print("Compression Completed")
input()
# endregion code
