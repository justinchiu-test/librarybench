def load_translations(locale):
    translations = {
        'en': {
            'greet': 'Hello',
            'farewell': 'Goodbye'
        },
        'es': {
            'greet': 'Hola',
            'farewell': 'Adiós'
        }
    }
    return translations.get(locale, {})
