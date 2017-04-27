import sys
import os
import sqlite3

def help():
    return '''\
{0} - create shortcuts for commands

Usage:

{0} <shortcut>           Print original command
{0} <shortcut>=<command> Define a shortcut for the given command
{0} -h                   Print this help
'''

PROG_NAME = os.path.basename(sys.argv[0])

home_dir = os.environ.get('BATIFY_HOME', '.')
work_dir = os.path.join(home_dir, 'exec')
db_file = os.path.join(home_dir, 'shortcuts.db')

output_script='''\
@echo off
{} %*'''

cmds = None
alias_cmd = None
orig_cmd = None

# Create directory structure in the current directory if it doesn't exists.
if not os.path.exists(work_dir):
    try:
        os.makedirs(work_dir)
    except:
        print("Oops! Could not create '{}`.".format(work_dir))
        sys.exit(1)

conn = sqlite3.connect(db_file)

cursor = conn.cursor()

cursor.execute('''\
CREATE TABLE IF NOT EXISTS shortcut (
    alias_cmd TEXT PRIMARY KEY,
    orig_cmd  TEXT NOT NULL
)
''')

conn.commit()

if len(sys.argv) > 2:
    print(help().format(PROG_NAME))
    sys.exit(1)
elif len(sys.argv) == 2 and sys.argv[1] == '-h':
    print(help().format(PROG_NAME))
    sys.exit(0)

# Print all aliases defined and exit.
if len(sys.argv) < 2:
    for row in cursor.execute('SELECT alias_cmd, orig_cmd from shortcut'):
        print('{}="{}"'.format(row[0], row[1]))
        
    sys.exit(0)
        
args = sys.argv[1].split('=')

# Show alias definition if it was defined.
if len(args) != 2:
    cursor.execute('''SELECT orig_cmd from shortcut
                    WHERE alias_cmd=?''', (args[0],))
    cmd = cursor.fetchone()
    if(not cmd):
        print("Error: alias `{}' not defined!".format(args[0]))
        sys.exit(1)
        
    print('{}="{}"'.format(args[0], cmd[0]))

# Define a new alias command.
else:
    alias_cmd = args[0]
    orig_cmd = args[1]

    try:
        cursor.execute('''INSERT INTO shortcut
                        (orig_cmd,alias_cmd) VALUES(?, ?)''',
                        (orig_cmd, alias_cmd))
    except:
        cursor.execute('''UPDATE shortcut
                        SET orig_cmd=? WHERE alias_cmd=?''',
                        (orig_cmd, alias_cmd))

    conn.commit()
    conn.close()

    with open('{}.bat'.format(os.path.join(work_dir, alias_cmd)), 'w') as batch:
        batch.write(output_script.format(orig_cmd))
