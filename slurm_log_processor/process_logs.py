import os
import re
import subprocess
import argparse
import warnings


def extract_job_id(log_file_content):
    """
    Extracts the job ID from the given log file content.

    Args:
        log_file_content (str): The content of the log file.

    Returns:
        str or None: The extracted job ID, or None if no match is found.
    """
    match = re.search(r"\bJobID\s+.*?\n.*?\n\s*(\d+)", log_file_content, re.DOTALL)
    # print(match)
    return match.group(1) if match else None


def get_sacct_output(job_id):
    """
    Gets the output of the 'sacct' command for a specific job ID.

    Args:
        log_file (str): The path to the log file.
        job_id (str): The ID of the job.

    Returns:
        str: The decoded output of the 'sacct' command.
    """
    sacct_command = f"sacct -j {job_id} --format=JobID,JobName,Partition,State,ExitCode,Start,End,Elapsed,NCPUS,NNodes,NodeList,ReqMem,MaxRSS,AllocCPUS,Timelimit,TotalCPU"
                             
    process = subprocess.Popen(
        sacct_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    output, _ = process.communicate()

    return output.decode()


def parse_sacct_output(sacct_output):
    """
    Parse the sacct output into a list.
    There are three rows of the standard output, but we are only interested in
    the first and second row which contain the job call information, and the
    the job usage information, respectively. We merge the information in these
    two rows into a single list for easier processing.

    Args:
        sacct_output (str): The standard output of the sacct command.
            containing the following columns:
            JobID, JobName, Partition, State, ExitCode, Start, End, Elapsed,
            NCPUS, NNodes, NodeList, ReqMem, MaxRSS, AllocCPUS, Timelimit,
            TotalCPU

    Returns:
        list: A list of strings containing the parsed information.
    """
    # Split the output into lines
    lines = sacct_output.strip().split("\n")

    # Use the second line (dashes) to determine column widths
    dash_line = lines[1]
    column_boundaries = []
    last_index = 0

    for match in re.finditer(r"-+", dash_line):
        start, end = match.span()
        column_boundaries.append((start, end))
        last_index = end

    # Parse each row according to the column boundaries
    parsed_rows = []
    for line in lines[2:]:  # Skip the header and separator lines
        row = [line[start:end].strip() for start, end in column_boundaries]
        parsed_rows.append(row)

    if len(parsed_rows) > 1:
        return [r1 if r1 else r2 for r1, r2 in zip(parsed_rows[0], parsed_rows[1])]
    else:
        return None


def collect_stats(sacct_output, stats_names):
    """
    Collects statistics from the sacct output based on the provided list of stat names.

    Args:
        sacct_output (list): The sacct output to parse.
        stats_names (list): The list of stat names to collect.

    Returns:
        dict: A dictionary containing the collected statistics, where the keys are the
        stat names and the values are the corresponding values from the sacct output.

    Raises:
        Warning: If a stat name is not found in the sacct output.
    """

    if not stats_names:
        return None
    stats = {}

    stats_names = [
        "JobID",
        "JobName",
        "Partition",
        "State",
        "ExitCode",
        "Start",
        "End",
        "Elapsed",
        "NCPUS",
        "NNodes",
        "NodeList",
        "ReqMem",
        "MaxRSS",
        "AllocCPUS",
        "Timelimit",
        "TotalCPU",
    ]

    sacct_output = parse_sacct_output(sacct_output)
    print(sacct_output)

    if sacct_output:
        for name in stats_names:
            try:
                index = stats_names.index(name)
                stats[name] = sacct_output[index]
            except ValueError:
                warnings.warn(
                    f'Stat "{name}" not found in sacct output. '
                    f"Please only use names from the following list: {all_names}"
                )
    return stats


def process_file(filepath, stats_names=None):
    """
    Process a file and extract relevant statistics.

    Args:
        filepath (str): The path to the file to be processed.
        stats_names (list, optional): A list of specific statistics to collect.
            Defaults to None.

    Returns:
        dict or str: A dictionary containing the extracted statistics if found,
        or "No stats found" if no statistics were found.
    """
    stats = None

    with open(filepath, "r") as file:
        content = file.read()
        job_id = extract_job_id(content)
        if job_id:
            stats = {"JobID": job_id}
            raw_output = get_sacct_output(job_id)
            if raw_output:
                stats.update(collect_stats(raw_output, stats_names))
            else:
                print("No sacct output found")

    return stats if stats else "No stats found"


import csv

def write_stats_to_file(stats, stats_file_name):
    """
    Write the statistics to a file using a CSV format. The rows will be the file names 
    and the columns will be the statistics.

    Args:
        stats (dict): A dictionary containing the statistics data.
        stats_file_name (str): The name of the file to write the statistics to.

    Returns:
        None
    """
    # Determine the maximum width for each column for pretty printing
    max_widths = {"FileName": max([len(filename) for filename in stats.keys()])}
    for details in stats.values():
        if details == "No stats found":
            continue
        for key, value in details.items():
            max_widths[key] = max(max_widths.get(key, len(key)), len(value))

    # Create and write to CSV file
    with open(stats_file_name, 'w', newline='') as file:
        headers = ["FileName"] + list(max_widths.keys())[1:]  # Exclude FileName since it's manually added
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for filename, details in stats.items():
            row = {'FileName': filename}
            for header in headers[1:]:
                try:
                    row[header] = details.get(header, "")
                except AttributeError:
                    row[header] = ""
            writer.writerow(row)



def process_log_files(directory, stats_names=None, stats_file=None):
    """
    Process log files in the specified directory and generate statistics
    usint the sacct command. Requires that the sacct command was alread called
    on the relevant file and that the JobID was stored in the log file.

    Args:
        directory (str): The directory path containing the log files.
        stats_names (list, optional): A list of specific statistics to calculate.
            Defaults to None.
        stats_file (str, optional): The file path to write the statistics to.
            Defaults to None.

    Returns:
        None
    """

    stats = {}
    for filename in os.listdir(directory):
        if filename.endswith(".log"):  # Assuming log files end with .log
            filepath = os.path.join(directory, filename)
            stats[filename] = process_file(filepath, stats_names)

    if stats_file:
        full_stats_file = os.path.abspath(stats_file)
        write_stats_to_file(stats, full_stats_file)


def main():
    parser = argparse.ArgumentParser(description="Process log files")

    parser.add_argument(
        "log_directory",
        type=str,
        help="Path to your log files",
    )
    parser.add_argument(
        "--stats",
        type=str,
        nargs="+",
        help="List of stats to extract",
        required=False,
    )
    parser.add_argument(
        "--stats-file-name",
        type=str,
        help="Path to the output file for the stats",
        required=False,
    )

    args = parser.parse_args()

    if args.stats_file_name and not args.stats:
        args.stats = ["JobID"]

    process_log_files(
        args.log_directory, stats_names=args.stats, stats_file=args.stats_file_name
    )


if __name__ == "__main__":
    main()
