#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py
Author: "Bassil Akar"
Semester: "Fall 2024"

The python code in this file is original work written by
"Bassil Akar". No code in this file is copied from any other source
except those provided by the course instructor, including any person,
textbook, or on-line resource. I have not shared this python script
with anyone or anything except for submission for grading.
I understand that the Academic Honesty Policy will be enforced and
violators will be reported and appropriate action will be taken.

Description: This script displays memory usage,
including total system memory usage or memory usage by specific processes.
It can display memory in a human-readable format.
'''

import argparse
import os, sys

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts", epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Prints sizes in human readable format")
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use if not.")
    args = parser.parse_args()
    return args

def percent_to_graph(percent: float, length: int=20) -> str:
    "Turns a percent 0.0 - 1.0 into a bar graph"
    filled_length = int(percent * length) # this line will calculate the number of #'s in the graph by multiplying the percentage by the total length and converting it to an integer
    return "#" * filled_length + " " * (length - filled_length) # this line will fill the graph bar with a string of (#) for thr filled portion and fill the rest with spaces.

def get_sys_mem() -> int:
    "Return total system memory (used or available) in kB"
    f = open('/proc/meminfo', 'r')
    try:
         for line in f:
             if line.startswith('MemTotal:'):
                return int(line.split()[1])
    except:
        f.close()

def get_avail_mem() -> int:
    "Return total memory that is available"
    f = open('/proc/meminfo', 'r')
    try:
         for line in f:
             if line.startswith('MemAvailable:'):
                return int(line.split()[1])
    except:
        f.close()

def pids_of_prog(app_name: str) -> list:
    "Given an app name, return all pids associated with app"
    pids = os.popen(f"pidof {app_name}").read().strip() # os.popen will let me use shell command and the pidof is a command that we use to get the pids of any app we searching for.
    return pids.split() if pids else [] # This line will retrun the pids and split i#I'm calculating the number of #'s in the graph by multiplying the percentage by the total length and converting it to an integert into a list & if the pids exsit the list of pids will appear if the pids is empty it will return an empty list.

def rss_mem_of_pid(proc_id: str) -> int:
    "Given a process id, return the resident memory used, zero if not found"
    try:
        f = open(f"/proc/{proc_id}/status", 'r') # It opens the file on read mode
        for line in f:
            if line.startswith('VmRSS:'):
                return int(line.split()[1]) #This line will return the line and split it into a list
        f.close()
    except FileNotFoundError:
        return 0 # If it didn't find the chosen entry then return 0

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "Turn 1,024 KiB into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    args = parse_command_args()
    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    used_mem = total_mem - avail_mem
    percent_used = used_mem / total_mem

    # memory size in human-readable format 
    if args.human_readable:
        total_mem_hr = bytes_to_human_r(total_mem)
        used_mem_hr = bytes_to_human_r(used_mem)
    else:
        total_mem_hr = f"{total_mem} kB"
        used_mem_hr = f"{used_mem} kB"

    if not args.program:
        # it will ignore or skip if no program is specified
        graph = percent_to_graph(percent_used, args.length) # create memory usage graph
        print(f"Memory         [{graph}| {percent_used * 100:.0f}%] {used_mem_hr}/{total_mem_hr}")
    else:
        pids = pids_of_prog(args.program)
        if not pids: # if pid is not found print the below line
            print(f"{args.program} not found.")

        total_rss_mem = 0
        for pid in pids:
            rss_mem = rss_mem_of_pid(pid)
            percent_rss = rss_mem / total_mem
            total_rss_mem += rss_mem
            graph = percent_to_graph(percent_rss, args.length)
            if args.human_readable: 
                rss_mem_hr = bytes_to_human_r(rss_mem)
            else:
                rss_mem_hr = f"{rss_mem} kB"
            print(f"{pid:<15} [{graph}| {percent_rss * 100:.0f}%] {rss_mem_hr}/{total_mem_hr}")

        if len(pids) > 1:
            # show total memory usage for multiple PIDs
            total_percent_rss = total_rss_mem / total_mem
            graph = percent_to_graph(total_percent_rss, args.length)
            if args.human_readable:
                total_rss_mem_hr = bytes_to_human_r(total_rss_mem)
            else:
                total_rss_mem_hr = f"{total_rss_mem} kB"
            print(f"{args.program:<15} [{graph}| {total_percent_rss * 100:.0f}%] {total_rss_mem_hr}/{total_mem_hr}")
