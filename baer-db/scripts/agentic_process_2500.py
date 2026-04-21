import glob
from os.path import split as _split
from os.path import join as _join
from os.path import exists as _exists
import xml.etree.ElementTree as ET
import datetime
import os
import re
import shutil
from pprint import pprint

def search_files(filepaths, tokens, threshold=2):
    scores = []
    patterns = [re.compile(re.escape(token), re.IGNORECASE) for token in tokens]
    for filepath in filepaths:
        fn = _split(filepath)[-1]
        score = 0
        for pattern in patterns:
            if pattern.search(fn):
                score += 1
        if score >= threshold:
            scores.append((filepath, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

def comparison_formatter(fn):
    return fn.upper().replace(' ', '').replace('/', '')

def process_reports(start_year=2024):
    date = datetime.datetime.now()
    
    # Path relative to scripts/
    directory_path = '../../raw_data/all_pdfs'
    projects_xml = '../Projects.xml'
    reports_dir = '../2500-8'
    logs_dir = 'logs'
    
    if not _exists(logs_dir):
        os.makedirs(logs_dir)

    assert _exists(directory_path), f"Directory not found: {directory_path}"
    assert _exists(projects_xml), f"Projects.xml not found: {projects_xml}"

    pdf_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(('.pdf', '.docx')):
                file_path = os.path.abspath(os.path.join(root, file))
                if '2500' in file:
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
    
    print(f'Found {len(pdf_files)} candidate source files')

    existing_reports = [_split(fn)[1] for fn in glob.glob(os.path.join(reports_dir, '*.*'))]

    tree = ET.parse(projects_xml)
    root = tree.getroot()
    
    projects_found = root.findall('Projects')
    print(f"Total projects in Projects.xml: {len(projects_found)}")

    log_path = f'logs/{date.year}-{date.month:02}-{date.day:02}_unmatched_2500.log'
    fp = open(log_path, 'w')

    matches_found = []
    missing_reports = []
    already_exists = []
    year_filtered = 0

    for project_elem in projects_found:
        fire_name = project_elem.find('Firename').text
        forest = project_elem.find('Forest').text
        
        if not fire_name or not forest:
            continue
            
        # Target filename
        target_fn_base = f'2500-8_{fire_name}_{forest}'.title().replace('/', ' ').replace(' ', '_')
        
        fire_start_elem = project_elem.find('FireStrt')
        if fire_start_elem is None or not fire_start_elem.text:
            continue

        fire_start = None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%m/%d/%y %H:%M:%S"):
            try:
                fire_start = datetime.datetime.strptime(fire_start_elem.text, fmt)
                break
            except ValueError:
                continue
                
        if fire_start is None:
            # print(f"Could not parse date: {fire_start_elem.text}")
            continue
            
        if fire_start.year < start_year:
            year_filtered += 1
            continue

        # Check if any version (pdf/docx) exists
        exists = False
        for ext in ['.pdf', '.docx']:
            if target_fn_base + ext in existing_reports:
                exists = True
                already_exists.append(target_fn_base + ext)
                break
        
        if exists:
            continue

        match = None
        # Strategy 1: exact fire name in filename (Finals)
        for rpt in finals:
            if comparison_formatter(fire_name) in comparison_formatter(_split(rpt)[1]):
                match = rpt
                break

        # Strategy 2: exact fire name in filename (Interims)
        if match is None:
            for rpt in interims:
                if comparison_formatter(fire_name) in comparison_formatter(_split(rpt)[1]):
                    match = rpt
                    break

        # Strategy 3: Token matching
        if match is None:
            tokens = fire_name.split() + forest.split()
            options = search_files(pdf_files, tokens, threshold=2)
            if options:
                # Automatically pick the top score if it's significantly better or the only one
                match = options[0][0]

        if match is not None:
            ext = os.path.splitext(match)[1]
            dest_fn = target_fn_base + ext
            dest_path = _join(reports_dir, dest_fn)
            
            if not _exists(dest_path):
                shutil.copyfile(match, dest_path)
                matches_found.append((fire_name, forest, _split(match)[1], dest_fn))
                print(f"MATCH: {fire_name} ({forest}) -> {dest_fn}")
        else:
            missing_reports.append((fire_name, forest, target_fn_base))
            print(f"MISSING: {fire_name} ({forest})")
            print(f"Firename: {fire_name}", file=fp)
            print(f"Forest: {forest}", file=fp)
            print(f"fire_start {fire_start}", file=fp)
            print("----", file=fp)

    fp.close()
    
    print("\n--- Summary ---")
    print(f"Total projects evaluated: {len(projects_found)}")
    print(f"Filtered out (pre-{start_year}): {year_filtered}")
    print(f"New matches copied: {len(matches_found)}")
    print(f"Reports still missing: {len(missing_reports)}")
    print(f"Reports already in {reports_dir}: {len(already_exists)}")
    
    return matches_found, missing_reports, already_exists

if __name__ == "__main__":
    process_reports(start_year=2024)
