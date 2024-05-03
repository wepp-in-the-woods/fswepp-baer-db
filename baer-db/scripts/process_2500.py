from glob import glob
from os.path import split as _split
from os.path import join as _join
from os.path import exists as _exists
from sqlalchemy import create_engine
import pandas as pd
import xml.etree.ElementTree as ET
import datetime
import os
import sys
import shutil

from pprint import pprint

date = datetime.datetime.now()

start_year = 2022

def comparison_formatter(fn):
    return fn.upper().replace(' ', '').replace('/', '')

# Directory path to search for .pdf files
directory_path = r'C:\Users\roger\Downloads\Dicks Work 2024\Dicks Work 2024\73 2500-8s'

# List to store the found .pdf file paths
pdf_files = []

# Traverse the directory tree
for root, dirs, files in os.walk(directory_path):
    for file in files:
        # Check if the file has a .pdf extension
        if file.endswith('.pdf'):
            # Construct the absolute file path
            file_path = os.path.join(root, file)

            if '2500' in file:
                # Append the file path to the list
                pdf_files.append(file_path)

finals = []
interims = []
for fn in pdf_files:
    base = _split(fn)[1].upper()
    if 'INITIAL' in base:
        continue
    if 'INTERIM' in base:
        interims.append(fn)
        continue

    finals.append(fn)
    
print(f'Found {len(pdf_files)} pdf_files')

assert len(pdf_files) > 0, "Did not find any pdf files to match make sure directory_path is set correctly."


reports = [_split(fn)[1] for fn in glob('../2500-8/*.pdf')]


# Parse the XML file
tree = ET.parse('../Projects.xml')
root = tree.getroot()


fp = open(f'logs/{date.year}-{date.month:02}-{date.day:02}_unmatched_2500.log', 'w')

# Iterate over "Project" elements
for project_elem in root.findall('Projects'):

    # Access and process project data
    fire_name = project_elem.find('Firename').text
    forest = project_elem.find('Forest').text
    fn = f'2500-8_{fire_name}_{forest}'.title() + '.pdf'
    fn = fn.replace('/', ' ')

    # Perform operations with project data
    if not fn in reports:

        fire_start = project_elem.find('FireStrt')

        if fire_start is None:
            continue

        fire_start = datetime.datetime.strptime(fire_start.text, "%Y-%m-%dT%H:%M:%S")
        
        if fire_start.year < start_year:
            continue

        match = None
        for rpt in finals:
            if comparison_formatter(fire_name) in  comparison_formatter(_split(rpt)[1]):
                match = rpt
                break

        if match is None:
            for rpt in interims:
                if comparison_formatter(fire_name) in  comparison_formatter(_split(rpt)[1]):
                    match = rpt
                    break

        if match is None:
            for rpt in pdf_files:
                if comparison_formatter(fire_name) in  comparison_formatter(_split(rpt)[1]):
                    match = rpt
                    break

        print(f"Firename: {fire_name}")
        print(f"Forest: {forest}")
        print(f"Report: {fn}")
        print(f"fire_start {fire_start}")
        print(f"Match: {match}")
        print("----")

        if match is not None:
            if not _exists(_join(f'../2500-8/{fn}')):
                shutil.copyfile(match, _join(f'../2500-8/{fn}'))
        else:
            print(f"Firename: {fire_name}", file=fp)
            print(f"Forest: {forest}", file=fp)
            print(f"Report: {fn}", file=fp)
            print(f"fire_start {fire_start}", file=fp)
            print(f"Match: {match}", file=fp)
            print("----", file=fp)

fp.close()
