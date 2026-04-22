import os

# Updated replacement_dict from export_tables.py
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
    "\u2026": "...", # Horizontal ellipsis '…'
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
    "Å": "", # Replication character
}

questionables_dict = {
    '>???': '>',
    '???\tPerennial': '        Perennial',
    '???\tIntermittent': '        Intermittent',
    'Pat McKinna????)': 'Pat McKinna)',
    '(???180 acres)': '(180 acres)'
}

def replace_non_ascii(xml_file_path):
    global replacement_dict
    
    if not os.path.exists(xml_file_path):
        print(f"File not found: {xml_file_path}")
        return

    print(f"Checking non-ASCII in {xml_file_path}...")
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    non_printables = set()
    for char in content:
        if not char.isprintable():
            if not char in ('\t', '\n'):
                non_printables.add(char)   
    
    if non_printables:
        for ch in non_printables:
            content = content.replace(ch, ' ')
        print(f'replace_non_ascii::Replaced {non_printables} non-printable characters')

    non_ascii = set([ch for ch in content if (not ord(ch) < 128) and (ch not in replacement_dict)])
    
    if non_ascii:
        print('Potentially problematic characters:')
        for ch in non_ascii:
            print(f"Character: '{ch}'\tUnicode: U+{ord(ch):04X}")
            
        print('replace_non_ascii::Aborting, please add problematic characters to the replacement_dict\n')
        return
    
    og_content = content
    for ch, new in replacement_dict.items():
        content = content.replace(ch, new)
    
    if og_content == content:
        print('replace_non_ascii::No replacements made\n')
        return
        
    with open(xml_file_path, 'w', encoding='utf-8') as file:
        file.write(content)
        
    print('replace_non_ascii::File modified in place\n')
    
def replace_questionables(xml_file_path):
    global questionables_dict
    
    if not os.path.exists(xml_file_path):
        return

    print(f"Checking questionables in {xml_file_path}...")
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    og_content = content
    
    for ch, new in questionables_dict.items():
        content = content.replace(ch, new)
        
    if '???' in content:
        print('Remaining questionables:')
        for line in content.split('\n'):
            if "???" in line:
                print(line)
                
    if og_content == content:
        print('replace_questionables::No questionable replacements made\n')
        return
        
    with open(xml_file_path, 'w', encoding='utf-8') as file:
        file.write(content)
        
    print('replace_questionables::File modified in place\n')
    
if __name__ == "__main__":
    xml_files = [
        'baer-db/Projects.xml',
        'baer-db/Treatments.xml',
        'baer-db/Treatment Costs.xml'
    ]
    
    # Adjust paths if run from within scripts/
    if os.path.basename(os.getcwd()) == 'scripts':
        xml_files = [os.path.join('..', f) for f in [
            'Projects.xml',
            'Treatments.xml',
            'Treatment Costs.xml'
        ]]

    for xml_file in xml_files:
        replace_non_ascii(xml_file)
        replace_questionables(xml_file)
