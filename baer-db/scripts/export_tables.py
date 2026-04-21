"""
This script exports Projects, Treatments, and Treatment Costs tables from the
MS Access Ebaer.accdb database into XML format compatible with the fswepp-baer-db project.

Prerequisites:
    - mdbtools (brew install mdbtools)
    - pandas (pip install pandas)

Usage:
    python3 baer-db/scripts/export_tables.py
"""
import subprocess
import pandas as pd
import io
import datetime
import os
import re

# Sanitization dictionaries from sanitize_characters.py
replacement_dict = {
    "\u00BD": "1/2", # 1/2 symbol '½'
    "\u00F6": "o", # Lowercase o with diaeresis 'ö'
    "\u00AD": "-", # Soft hyphen '­'
    "\u2010": "-", 
    "\u2014": "-", # Em dash '—'
    "\u2013": "-", # En dash '–'
    "\uF0A7": "-", # Bullet point (custom symbol) ''
    "\uF0D8": "???", # Right-pointing arrow (custom symbol) ''
    "\u00E9": "e", # Lowercase e with acute 'é'
    "\uF0FC": " ", # Check mark (custom symbol) ''
    "\u2248": "???", # Almost equal to '≈'
    "\u00F1": "n", # Lowercase n with tilde 'ñ'
    "\uF0AE": "???", # Rightwards arrow to bar (custom symbol) ''
    "\u00BC": "1/4", # 1/4 symbol '¼'
    "\u2026": "...", # Horizontal ellipsis '…' (updated from " ")
    "\u00BE": "3/4", # 3/4 symbol '¾'
    "\u201D": '"', # Right double quotation mark "”"
    "\u201C": '"', # Left double quotation mark "“"
    "\u2018": "'", # Left single quotation mark "‘"
    "\u2019": "'", # Right single quotation mark "’"
    "\u2022": "-", # Bullet "•"
    "\x02": " ",   # Access internal delimiter
    # Add CP1252 direct byte interpretations that commonly appear in Access/mdbtools latin-1 output
    "\x80": "EUR", # Euro
    "\x82": "'",   # Low-9 quote
    "\x83": "f",   # Florin
    "\x84": '"',   # Low-9 double quote
    "\x85": "...", # Ellipsis
    "\x88": "^",   # Circumflex
    "\x89": "per mille",
    "\x8a": "S",   # S hachek
    "\x8b": "<",   # Left guillemet
    "\x8c": "OE",  # OE ligature
    "\x91": "'",   # Smart single quote
    "\x92": "'",   # Smart single quote
    "\x93": '"',   # Smart double quote
    "\x94": '"',   # Smart double quote
    "\x95": "-",   # Bullet
    "\x96": "-",   # En dash
    "\x97": "-",   # Em dash
    "\x98": "~",   # Tilde
    "\x99": "TM",  # Trademark
    "\x9a": "s",   # s hachek
    "\x9b": ">",   # Right guillemet
    "\x9c": "oe",  # oe ligature
    "\x9d": " ",   # undefined
    "\x9f": "Y",    # Y diaeresis
    # Fallbacks for characters reported by sanitize_characters.py
    "Â": "", 
    "â": "...",
    "Ã": "A",
    "§": "Section",
    "®": "(R)",
    "©": "(C)",
    "™": "(TM)",
    "±": "+/-",
    "¢": "cents",
    "·": "-",
    "ï": "i",
    "¦": "|",
    "¯": "-",
    "¶": "P",
}

questionables_dict = {
    '>???': '>',
    '???\tPerennial': '        Perennial',
    '???\tIntermittent': '        Intermittent',
    'Pat McKinna????)': 'Pat McKinna)',
    '(???180 acres)': '(180 acres)'
}

def clean_column_name(name):
    # MS Access XML export replaces spaces and special characters with _x00HH_
    # Tag names can only contain alphanumeric characters, underscores, hyphens, and dots.
    # We replace everything else with _x00HH_ where HH is the hex value.
    
    def replace_char(match):
        char = match.group(0)
        return f"_x00{ord(char):02X}_"

    # Match any character that is not alphanumeric or underscore
    # (Simplified set for safety in XML element names)
    cleaned = re.sub(r'[^a-zA-Z0-9_]', replace_char, name)
    return cleaned

def escape_xml(val):
    if val is None:
        return ""
    str_val = str(val)
    return str_val.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

def sanitize_string(s):
    if not isinstance(s, str):
        return s
    
    # 1. Replace non-printable characters (except \n, \t)
    chars = []
    for char in s:
        if char.isprintable() or char in ('\n', '\t'):
            chars.append(char)
        else:
            chars.append(' ')
    s = "".join(chars)
    
    # 2. Use replacement_dict
    for old, new in replacement_dict.items():
        s = s.replace(old, new)
        
    # 3. Use questionables_dict
    for old, new in questionables_dict.items():
        s = s.replace(old, new)
        
    return s

def export_table_to_ms_xml(db_path, table_name, output_path):
    print(f"Exporting {table_name} to {output_path}...")
    
    # 1. Get CSV data from mdb-export
    raw_data = subprocess.check_output(["mdb-export", db_path, table_name])
    csv_data = raw_data.decode("latin-1")
    
    # Normalize line endings
    csv_data = csv_data.replace('\r\n', '\n').replace('\r', '\n')
    
    # 2. Load into Pandas
    df = pd.read_csv(io.StringIO(csv_data))
    
    # Clean column names to match MS Access style
    df.columns = [clean_column_name(col) for col in df.columns]
    row_name = clean_column_name(table_name)
    
    # 3. Generate XML with MS Access specific metadata
    generated_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    xml_header = f'<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_header += f'<dataroot xmlns:od="urn:schemas-microsoft-com:officedata" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  generated="{generated_time}">\n'
    
    rows_xml = []
    for _, row in df.iterrows():
        row_xml = f"<{row_name}>\n"
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                continue
            
            # Sanitize and escape
            sanitized_val = sanitize_string(val)
            row_xml += f"<{col}>{escape_xml(sanitized_val)}</{col}>\n"
        row_xml += f"</{row_name}>\n"
        rows_xml.append(row_xml)
    
    footer = "</dataroot>"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_header)
        f.writelines(rows_xml)
        f.write(footer)
    
    print(f"Finished exporting {table_name}.")

if __name__ == "__main__":
    db = "fswepp-baer-db/baer-db/Ebaer.accdb"
    
    tables_to_export = {
        "Projects": "fswepp-baer-db/baer-db/Projects.xml",
        "Treatments": "fswepp-baer-db/baer-db/Treatments.xml",
        "Treatment Costs": "fswepp-baer-db/baer-db/Treatment Costs.xml"
    }
    
    for table, path in tables_to_export.items():
        if os.path.exists(db):
            try:
                export_table_to_ms_xml(db, table, path)
            except Exception as e:
                print(f"Error exporting {table}: {e}")
        else:
            print(f"Database not found at {db}")
