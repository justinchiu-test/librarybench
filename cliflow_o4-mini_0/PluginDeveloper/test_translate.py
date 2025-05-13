from plugin_framework.decorators import translate
from plugin_framework.i18n import set_locale, add_translation

def test_translate_decorator():
    set_locale('es')
    add_translation('es', 'hello', 'hola')
    @translate
    def greet():
        return 'hello'
    assert greet() == 'hola'
