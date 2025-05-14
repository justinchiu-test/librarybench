from clinical_researcher.form_system.renderer import CursesRenderer
from clinical_researcher.form_system.fields import TextField

def test_render_basic():
    form = {
        'f1': TextField('Field1', placeholder='p1'),
        'f2': TextField('Field2', placeholder='p2'),
    }
    rend = CursesRenderer(form)
    output = rend.render()
    assert '[Field1](p1)' in output
    assert '[Field2](p2)' in output
    assert '\t' in output
    assert not output.startswith('ACCESSIBLE:')

def test_render_accessible():
    form = {'f': TextField('F', placeholder='')}
    rend = CursesRenderer(form)
    rend.accessibility_mode = True
    output = rend.render()
    assert output.startswith('ACCESSIBLE:')
