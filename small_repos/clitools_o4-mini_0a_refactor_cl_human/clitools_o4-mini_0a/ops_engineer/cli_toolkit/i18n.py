def load_translations(po_file):
    """
    Load .po file translations into a dict {msgid: msgstr}
    """
    translations = {}
    try:
        with open(po_file, 'r', encoding='utf-8') as f:
            msgid = None
            for line in f:
                line = line.strip()
                if line.startswith('msgid '):
                    msgid = line.split('msgid ')[1].strip().strip('"')
                elif line.startswith('msgstr ') and msgid is not None:
                    msgstr = line.split('msgstr ')[1].strip().strip('"')
                    translations[msgid] = msgstr
                    msgid = None
    except FileNotFoundError:
        raise
    return translations
