"""
I18n loader for data_scientist datapipeline CLI.
"""
def load_translations(locale):
    translations = {}
    if locale == 'en':
        translations['greet'] = 'Hello'
    elif locale == 'es':
        translations['farewell'] = 'Adiós'
    return translations