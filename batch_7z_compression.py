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
# region user parameters
save_path = ""
file_name = "compression_results"
test_archive = True
retry_failure = True
retry_attempts = 1
log = True
csv = True
# endregion user parameters
# region code

# If the save path is empty use current working directory
if save_path == "":
    save_path = Path.cwd()
# Create the full output path
log_path = Path(save_path, f"{file_name}.log")
save_path = Path(save_path, f"{file_name}.csv")

# Data frame to hold stats
frame = pd.DataFrame(
    columns=[
        "Name",
        "Type",
        "Path",
        "Last Modification",
        "Start",
        "End",
        "Elapsed",
        "Status",
        "Tested",
        "Attempt Number",
        "Uncompressed",
        "Compressed",
        "Savings",
        "Ratio",
    ]
)


# Printing  and saving to log
def print_log(message):
    # Print to console
    print(message)
    # Save to file
    if log == True:
        with open(log_path, "a+") as file:
            file.write(f"{message}\n")


# Gets formatted datetime
def formatted_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")


# If the user has failed you end yourself
def exit_compression(say):
    # If on windows run the cls command to clear the terminal
    if os.name == "nt":
        os.system("cls")
    # If on linux run the cls command to clear the terminal
    else:
        os.system("clear")
    # Send a message
    print_log(say)
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
        if passed_path.is_dir():
            return passed_path
        else:
            exit_compression("Passed path isn't a valid directory.")


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
    if delete_path.exists():
        if delete_type == "File":
            os.remove(delete_path)
        elif delete_type == "Directory":
            shutil.rmtree(delete_path)
        print_log(f'Deleted the {delete_type} at "{delete_path}"')
    else:
        print_log(f'Couldn\'t find or delete the {delete_type} at "{delete_path}"')


# Records the entry to a data frame
def record_entry(
    name,
    object_type,
    full_path,
    last_modification,
    start_time,
    check_archive,
    tested,
    attempt_number,
    sizes,
):
    # Get statistics!
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time

    # Modifying for printing
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S:%f")
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S:%f")
    elapsed_time = datetime.datetime.utcfromtimestamp(
        elapsed_time.total_seconds()
    ).strftime("%H:%M:%S:%f")
    last_modification = last_modification.strftime("%Y-%m-%d %H:%M:%S:%f")

    # Savings
    savings = sizes[0] - sizes[1]
    # Using a try instead of if sizes[0] == 0
    try:
        ratio = sizes[1] / sizes[0]
    except:
        ratio = 0

    # Save Stats
    entry = np.array(
        [
            name,
            object_type,
            full_path,
            last_modification,
            start_time,
            end_time,
            elapsed_time,
            check_archive,
            tested,
            attempt_number,
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


# Writes the entry to a csv
def write_entry(write_type):
    if csv == True:
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


# Gets the size of files and directories
def get_size(object_type, path_to):
    # To store result
    size = 0
    # Get the size for files
    if object_type == "File":
        # size = os.path.getsize(path_to)
        size = os.stat(path_to).st_size
    # Get the size for directories
    elif object_type == "Directory":
        temp_size = 0
        # For every item in the directory
        for inside in os.scandir(path_to):
            # If it's a file, just get the size :^)
            if inside.is_file():
                # temp_size += os.path.getsize(inside)
                temp_size += os.stat(inside).st_size
            # If it's a directory, time for recursion
            elif inside.is_dir():
                temp_size += get_size("Directory", inside.path)
        # Set the final size
        size = temp_size
    # Return the size
    return size


# Gets the age of files and directories
def get_age(object_type, path_to):
    # To store result
    last_modification = ""
    # Get the size for files
    if object_type == "File":
        last_modification = os.stat(path_to).st_mtime
        last_modification = datetime.datetime.utcfromtimestamp(last_modification)
    # Get the size for directories
    elif object_type == "Directory":
        temp_age = datetime.datetime.utcfromtimestamp(0)
        # For every item in the directory
        for inside in os.scandir(path_to):
            # If it's a file check the age compared to the temp age
            if inside.is_file():
                temp_modification = os.stat(inside).st_mtime
                temp_modification = datetime.datetime.utcfromtimestamp(
                    temp_modification
                )
                # If the temp_modification is younger then replace it
                if temp_modification > temp_age:
                    temp_age = temp_modification
            # If it's a directory, time for recursion
            elif inside.is_dir():
                temp_modification = get_age("Directory", inside.path)
                # If the temp_modification is younger then replace it
                if temp_modification > temp_age:
                    temp_age = temp_modification
        # Set the final size
        last_modification = temp_age
    # Return the size
    return last_modification


# Compress the file
def compression(base_path, full_path, object_type, attempt_number):
    # Start time of the compression
    start_time = datetime.datetime.now()
    # Print logs
    print_log("====================================")
    print_log(
        f'Beginning to archive the {object_type} at "{full_path}"on attempt {attempt_number} at {formatted_datetime()}'
    )
    # Variable to store results
    sizes = [0, 0]
    check_archive = "No"
    tested = "No"
    # Get the name for statistics
    name = full_path.name
    # Get the stem of the item to be encrypted
    stem = full_path.stem
    output_path = Path(base_path, f"{stem}.7z")
    # Run 7z to create an archive
    archive_result = subprocess.run(
        ["7z", "a", f"{output_path}", f"{full_path}"],
        shell=False,
        capture_output=True,
        text=True,
    )
    archive_out = archive_result.stdout.split("\n")
    check_archive = check_success(archive_out[-2:])
    # Check if the file archived successfully
    if check_archive == "Passed":
        # Get the age
        last_modification = get_age(object_type, full_path)
        # Get the raw size
        sizes[0] = get_size(object_type, full_path)
        # Get the compressed size
        sizes[1] = get_size("File", output_path)
        # Print log
        print_log(
            f'Archive of the {object_type} at "{full_path}" was successful on attempt {attempt_number} at {formatted_datetime()} from {last_modification.strftime("%Y-%m-%d %H:%M:%S:%f")}'
        )
        # If the we want to test the archive as well
        if test_archive == True:
            # Print log
            print_log(
                f'Testing the archive at "{output_path}" at {formatted_datetime()}'
            )
            # Run the 7z test
            test_result = subprocess.run(
                ["7z", "t", f"{output_path}"],
                shell=False,
                capture_output=True,
                text=True,
            )
            # List of all the lines from the result
            test_out = test_result.stdout.split("\n")
            # Check for the success of the test (Think I can safely limit the results down to this range)
            check_test = check_success(test_out[8:-4])
            # Change test results
            tested = check_test
            # If the archive passed
            if check_test == "Passed":
                # Print log
                print_log(
                    f'Test of the archive at "{output_path}" was successful on attempt {attempt_number} at {formatted_datetime()}'
                )
                # Delete the source file/directory
                delete(object_type, full_path)
            # If the archive failed
            elif check_test == "Failed":
                # Print log
                print_log(
                    f'Test of the archive at "{output_path}" was unsuccessful on attempt {attempt_number} at {formatted_datetime()}'
                )
                # Remove the failed 7z file
                delete("File", output_path)
                # Write to csv
                record_entry(
                    name,
                    object_type,
                    full_path,
                    last_modification,
                    start_time,
                    check_archive,
                    tested,
                    attempt_number,
                    sizes,
                )
                if retry_failure == True:
                    print_log(
                        f'Retrying to archive the {object_type} at "{full_path}" was unsuccessful at {formatted_datetime()}'
                    )
                    return "Retry"
                else:
                    return "Skip"
        # If we're not testing the archive
        else:
            # Delete the source file/directory
            delete(object_type, full_path)
    # The archive didn't pass. Remove it and try again or skip to next
    else:
        # Print log
        print_log(
            f'Archive of the {object_type} at "{full_path}" was unsuccessful on attempt {attempt_number} at {formatted_datetime()}'
        )
        # Remove the failed 7z file
        delete("File", output_path)
        # Write to csv
        record_entry(
            name,
            object_type,
            full_path,
            last_modification,
            start_time,
            check_archive,
            tested,
            attempt_number,
            sizes,
        )
        if retry_failure == True:
            print_log(
                f'Retrying to archive the {object_type} at "{full_path}" at {formatted_datetime()}'
            )
            return "Retry"
        else:
            return "Skip"
    # Write to csv
    record_entry(
        name,
        object_type,
        full_path,
        last_modification,
        start_time,
        check_archive,
        tested,
        attempt_number,
        sizes,
    )


# For every object in the directory
def begin_compression():
    # Get the directory
    designated_path = check_for_path()
    # Create the csv for stat storage if it doesn't already exist (and the path exists)
    write_entry("Create")
    # Get the items in the directory
    items = os.listdir(designated_path)
    # For every item in the directory
    for entry in items:
        # For recording retry counts
        current_attempt = 1
        # Get the current items full path
        full_item = Path(designated_path, entry)
        # Check if the item is a directory or file
        if full_item.is_file():
            # Get the extension type
            extension = full_item.suffix
            # If the file isn't already a 7z then compress it
            if extension != ".7z":
                # Compress the file
                compression_result = compression(
                    designated_path, full_item, "File", current_attempt
                )
                # If the compression result failed then retry it or skip it
                if (
                    compression_result == "Retry"
                    and current_attempt < retry_attempts + 1
                ):
                    compression_result = compression(
                        designated_path, full_item, "File", current_attempt
                    )
            else:
                print_log("====================================")
                print_log(
                    f'7z File Skipped at "{designated_path}" at {formatted_datetime()}'
                )
        elif full_item.is_dir():
            # Compress the directory
            compression_result = compression(
                designated_path, full_item, "Directory", current_attempt
            )
            # If the compression result failed then retry it or skip it
            if compression_result == "Retry" and current_attempt < retry_attempts + 1:
                compression_result = compression(
                    designated_path, full_item, "File", current_attempt
                )


# Begin the actual main function
begin_compression()
# Print final result
print_log("====================================")
print_log("Compression Completed")
print_log("====================================")
# Close after next input
input()
# endregion code
