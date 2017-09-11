#!/usr/bin/env python

import argparse 
import os
import os.path
import exifread
from termcolor import colored

# Parse arguments pretty
parser = argparse.ArgumentParser(description='photorec post-recover utils.')

# Required parameters
parser.add_argument('folders', metavar='folder', type=str, nargs='+', help='Source folders.')

# Optional parameters
parser.add_argument('-r','--recursive', dest='recursive', help='Perform a recursive search inside directories.')
parser.add_argument('-v','--verbose', dest='verbose', help='Verbose output.', action='store_true')
parser.add_argument('-ms','--min_size', dest='min_size', help='Match files with size greater or equal than this value.')
parser.add_argument('-Ms','--max_size', dest='max_size', help='Match files with size lower or equal than this value.')

# Modes
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-f', '--find', dest='find', help='Find specific files.', action='store_true')
group.add_argument('-s', '--sort', dest='sort', help='Sort files.', action='store_true')

# Search modes
group = parser.add_mutually_exclusive_group()
group.add_argument('-re', '--regex', dest='regex', help='Regex pattern for matching filenames.')
group.add_argument('-m', '--match', dest='match', help='Match substring in filenames.')

args = parser.parse_args()

# Banner
print(colored("photorec post-recover utils.\n", attrs=['bold']))


def error(err):
    print(colored("[ERROR] ", "red") + err)

def warning(err):
    print(colored("[WARN] ", "yellow") + err)

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'k', 'm', 'g', 't', 'p', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

def scan_dir(folder):
    if(not os.path.exists(folder)):
        error(folder + ' is not a valid directory.')

    for root, dirs, files in os.walk(folder, topdown=False):
        for file in files:
            print(file)

def find_files(folders, match, regex, verbose, min_size, max_size):

    for folder in folders:
        print('searching for files in:')
        print(colored(folder, attrs=['bold']))
        
        if(not os.path.exists(folder)):
            error(folder + ' is not a valid directory.')

    # Finds matching filenames
    if(match is None and regex is None):
        error("you must specify a search pattern")
        error("use -re/--regex or -m/--match options")

    # Search by substring text match
    if(match is not None):
        print("searching by text match " + colored("%" + match + "%", attrs=['bold']))
        for root, dirs, files in os.walk(folder, topdown=False):
            for file in files:
                if(match is not None):
                    file_info = os.stat(folder + file)
                    
                    # Check substring match
                    if match in file:

                        # Check size filters
                        if((min_size is None or file_info.st_size >= eval(min_size)) and (max_size is None or file_info.st_size <= eval(max_size))):

                            # Print found file
                            print('{:s} [{:s}]'.format(file, sizeof_fmt(file_info.st_size)))

                            # Get file extension
                            filename, file_extension = os.path.splitext(file)

                            # Get exif data if its an image
                            try: 
                                if(file_extension in [".png", ".jpg"]):
                                    exif_tags = exifread.process_file(file, details=True)
                                    print(exif_tags)
                            except:
                                if(verbose):
                                    warning("invalid exif tags for " + file)
                # Search by regex
                if regex is not None:
                    pass
        print("")

    # Search by regex pattern
    if(regex is not None):
        print("searching by regex match ")

if(args.find):
    find_files(folders=args.folders, match=args.match, regex=args.regex, verbose=args.verbose, min_size=args.min_size, max_size=args.max_size)