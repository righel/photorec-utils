#!/usr/bin/env python

import argparse 
import os
import os.path
from shutil import copyfile
import cv2
import exifread
from termcolor import colored
import colorama
import numpy as np
from matplotlib import pyplot as plt

# Parse arguments pretty
parser = argparse.ArgumentParser(description='photorec post-recover utils.')

# Required parameters
parser.add_argument('dirs', metavar='dir', type=str, nargs='+', help='Source dirs.')

# Optional parameters
parser.add_argument('-r','--recursive', dest='recursive', help='Perform a recursive search inside directories.', action='store_true')
parser.add_argument('-v','--verbose', dest='verbose', help='Verbose output.', action='store_true')
parser.add_argument('-ms','--min_size', dest='min_size', help='Match files with size greater or equal than this value.')
parser.add_argument('-Ms','--max_size', dest='max_size', help='Match files with size lower or equal than this value.')
parser.add_argument('-o','--output', dest='output', help='Output folder for copying results.')

# Search modes
group = parser.add_mutually_exclusive_group()
group.add_argument('-re', '--regex', dest='regex', help='Regex pattern for matching filenames.')
group.add_argument('-m', '--match', dest='match', help='Match substring in filenames.')

args = parser.parse_args()

# Init term colors
colorama.init()

# Banner
print(colored("photorec post-recover utils.\n", attrs=['bold']))

# Constants
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp"]

def error(err):
    print(colored("[ERROR] ", "red") + err)

def warning(err):
    print(colored("[WARN] ", "yellow") + err)

def histogram(filename):
    print(filename)
    img = cv2.imread(filename, 0)
    ravel = img.ravel()
    # print(ravel)
    
    size = np.shape(img) 
    
    non_zeros = np.count_nonzero(img)
    total_pixels = float(size[0] * size[1])
    zeros = float(total_pixels - non_zeros)
    zeros_ratio = zeros / total_pixels
    print(zeros_ratio)

    plt.hist(ravel, 256, [0,256])
    plt.show()

    # color = ('b','g','r')
    # for i,col in enumerate(color):
    #     histr = cv2.calcHist([img],[i],None,[256],[0,256])
    #     plt.plot(histr,color = col)
    #     plt.xlim([0,256])
    # plt.show()

def blackness(filename, verbose):
    img = cv2.imread(filename, 0)

    size = np.shape(img) 
    
    non_zeros = np.count_nonzero(img)
    total_pixels = float(size[0] * size[1])
    zeros = float(total_pixels - non_zeros)
    zeros_ratio = zeros / total_pixels

    if(verbose):
        print("blackness: {0:.2f}".format(zeros_ratio))

    return zeros_ratio

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'k', 'm', 'g', 't', 'p', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

def find_files(dir, match, regex, verbose, min_size, max_size):
    matched = 0

    print('searching for files in ' + colored(dir, attrs=['bold']))
    
    if(not os.path.isdir(dir)):
        error(dir + ' is not a valid directory.')

    # Finds matching filenames
    if(match is None and regex is None):
        error("you must specify a search pattern")
        error("use -re/--regex or -m/--match options")

    # Search by substring text match
    if(match is not None):
        print("searching by text match " + colored("%" + match + "%", attrs=['bold']))
        for root, subdirs, files in os.walk(dir, topdown=False):
            
            for file in files:
                full_filename = os.path.join(root, file)
                if(match is not None):

                    # Check substring match
                    if match in file:
                    
                        try:
                            file_info = os.stat(full_filename)
                        except:
                            warning("couldn't get file info for: " + file)
                            continue
                    

                        # Check size filters
                        if((min_size is None or file_info.st_size >= eval(min_size)) and (max_size is None or file_info.st_size <= eval(max_size))):

                            # Get file extension
                            filename, file_extension = os.path.splitext(file)

                            # Get exif data if its an image
                            try: 
                                if(file_extension.lower() in IMAGE_EXTENSIONS):
                                    exif_tags = exifread.process_file(file, details=True)
                                    if(verbose):
                                        print(exif_tags)
                            except:
                                if(verbose):
                                    warning("invalid exif tags for " + file)

                            # Check image filters
                            # # Blackness of the image
                            # try:
                            #     if(file_extension.lower() in IMAGE_EXTENSIONS):
                            #         if(blackness(full_filename, verbose) < 0.65):
                            #             continue
                            # except:
                            #     error("Couldn't compute blackness for " + file)
                            #     continue

                            # If all matches, print found filename
                            matched = matched + 1
                            print('{:s} [{:s}]'.format(file, sizeof_fmt(file_info.st_size)))
                            
                            # Copy file if output dir is present
                            if (args.output is not None):
                                dst_dir = os.path.join(os.getcwd(), args.output)

                                # Create dir if doesn't exists
                                if(not os.path.isdir(dst_dir)):
                                    os.mkdir(dst_dir)

                                # Copy file
                                dst_file = os.path.join(dst_dir, file)
                                copyfile(full_filename, dst_file)

                # Search by regex
                if regex is not None:
                    pass
            
            # Print matched files
            print("\n" + colored("Matched files: {:d}".format(matched), attrs=['bold']))
            
            # Recursive walk inside paths
            if subdirs is not None and args.recursive:
                for subdir in subdirs:
                    if(os.path.isdir(subdir)):
                        find_files(subdir, match, regex, verbose, min_size, max_size)
            

    # Search by regex pattern
    if(regex is not None):
        print("searching by regex match ")

for dir in args.dirs:
    find_files(dir=dir, match=args.match, regex=args.regex, verbose=args.verbose, min_size=args.min_size, max_size=args.max_size)