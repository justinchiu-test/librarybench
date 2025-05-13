def prompt_interactive():
    name = input("Enter your name: ")
    dept = input("Enter your department: ")
    software = input("Enter software to install (comma separated): ")
    licenses = input("Enter license keys (comma separated): ")
    return {
        'name': name,
        'department': dept,
        'software': [s.strip() for s in software.split(',') if s.strip()],
        'licenses': [l.strip() for l in licenses.split(',') if l.strip()],
    }
