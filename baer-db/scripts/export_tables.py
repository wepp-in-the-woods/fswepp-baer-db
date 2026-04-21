import subprocess
import pandas as pd
import io
import datetime
import os
import re

def clean_column_name(name):
    # MS Access XML export replaces spaces and special characters with _x00HH_
    name = name.replace(' ', '_x0020_')
    name = name.replace('#', '_x0023_')
    return name

def escape_xml(val):
    if val is None:
        return ""
    str_val = str(val)
    return str_val.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

def export_table_to_ms_xml(db_path, table_name, output_path):
    print(f"Exporting {table_name} to {output_path}...")
    
    # 1. Get CSV data from mdb-export
    # Using latin-1 as it covers common Windows-1252 characters used in Access
    # which often cause UTF-8 decode errors (like smart quotes)
    raw_data = subprocess.check_output(["mdb-export", db_path, table_name])
    csv_data = raw_data.decode("latin-1")
    
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
            
            row_xml += f"<{col}>{escape_xml(val)}</{col}>\n"
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
