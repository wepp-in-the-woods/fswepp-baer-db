replacement_dict = {
    "\u00BD": "1/2", # 1/2 symbol '½'
    "\u00F6": "o", # Lowercase o with diaeresis 'ö'
    "\u00AD": "-", # Soft hyphen '­'
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
    "\u2026": " ", # Horizontal ellipsis '…'
    "\u00BE": "3/4", # 3/4 symbol '¾'
    "\u201D": '"', # Right double quotation mark "”"
    "\u201C": '"', # Left double quotation mark "“"
    "\u2018": "'", # Left single quotation mark "‘"
    "\u2019": "'", # Right single quotation mark "’"
    "\u2022": "-"  # Bullet "•"
}

def replace_non_ascii(xml_file_path):
    global replacement_dict
    
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    non_printables = set()
    for i, char in enumerate(content):
        if not char.isprintable():
            if not char in ('\t', '\n'):
                non_printables.add(char)   
    
    if non_printables:
        for ch in non_printables:
            content = content.replace(ch, ' ')
        print(f'\nreplace_non_ascii::Replaced {non_printables} non-printable characters\n\n')

    non_ascii = set([ch for ch in content if (not ord(ch) < 128) and (ch not in replacement_dict)])
    
    if non_ascii:
        print('Potentially problematic characters:')
        for ch in non_ascii:
            print(f"Character: '{ch}'\tUnicode: U+{ord(ch):04X}")
            
        print('\nreplace_non_ascii::Aborting, please add problematic characters to the replacement_dict\n\n')
        return
    
    og_content = f'{content}'
    for ch, new, in replacement_dict.items():
        content = content.replace(ch, new)
    
    if og_content == content:
        print('\nreplace_non_ascii::No replacements made\n\n')
        return
        
    with open(xml_file_path, 'w', encoding='utf-8') as file:
        file.write(content)
        
    print('\nreplace_non_ascii::File modified in place\n\n')
    
questionables_dict = {
    '>???': '>',
    '???\tPerennial': '        Perennial',
    '???\tIntermittent': '        Intermittent',
    'Pat McKinna????)': 'Pat McKinna)',
    '(???180 acres)': '(180 acres)'
}

def replace_questionables(xml_file_path):
    global questionables_dict
    
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    og_content = f'{content}'
    
    for ch, new, in questionables_dict.items():
        content = content.replace(ch, new)
        
    if '???' in content:
        print('Remaining questionables:')
        remaining_questionables = []
        for line in content.split('\n'):
            if "???" in line:
                print(line)
                
    if og_content == content:
        print('\nreplace_questionables::No questionable replacements made\n\n')
        return
        
    with open(xml_file_path, 'w', encoding='utf-8') as file:
        file.write(content)
        
        
    print('\nreplace_questionables::File modified in place')
    
if __name__ == "__main__":
    # 1. export Projects.xml from .accdb
    
    # 2. git commit Projects.xml 
    
    # 3. run the replacements pass
    xml_file_path = '../Projects.xml'
    replace_non_ascii(xml_file_path)

    # 4. view git diff to see changes
    
    # 5. resolve questionables by adding to questionables_dict
    
    # 6. add replacements to the questionables_dict
    replace_questionables(xml_file_path)