
import re

TYPE_MAP = {
    'varchar': 'TEXT',
    'date': 'TEXT',
    'datetime': 'TEXT',
    'longtext': 'TEXT',
    'int': 'INTEGER',
    'text': 'TEXT',
    'decimal': 'REAL'
}

COLUMN_TEMPLATE = {
    'name': '[name] TEXT NOT NULL UNIQUE PRIMARY KEY',
    'creation': '[creation] TEXT',
    'modified': '[modified] TEXT',
    'modified_by': '[modified_by] TEXT',
    'owner': '[owner] TEXT',
    'docstatus': '[docstatus] INTEGER',
    'parent': '[parent] TEXT',
    'parentfield': '[parentfield] TEXT',
    'parenttype': '[parenttype] TEXT',
    'idx': '[idx] INTEGER'
}

pattern = re.compile(r'`([^`]+)` ([^( ]+)([^,]+)?')


def append(line):
    with open('./master-lite.sql', 'a') as f:
        f.write(line.replace(r"\'", '"') + '\n')


with open('./master-lite.sql', 'w') as f:
    pass


def cleanup_stmt(line):
    counter = 1
    while '`' in line:
        line = line.replace('`', ']' if not (counter % 2) else '[', 1)
        counter += 1
    return line


def cleanup(line):
    #counter = 1
    #while '`' in line:
    #    line = line.replace('`', ']' if not (counter % 2) else '[', 1)
    #    counter += 1

    match = pattern.match(line)
    if match:
        column = match.group(1).strip()
        columntype = match.group(2).strip()

        if column in COLUMN_TEMPLATE:
            line = COLUMN_TEMPLATE[column]
        else:
            line = ' '.join([f'[{column}]', TYPE_MAP.get(columntype, columntype)])

    return line


with open('./master.sql', 'r') as f:
    active_table = None
    indexes = []
    columns = []

    for line in f:
        line = line.strip()

        if not line:
            continue

        elif line.startswith('--'):
            continue

        elif line.startswith('/*!'):
            continue

        elif line.startswith('LOCK TABLES'):
            continue

        elif line.startswith('UNLOCK TABLES'):
            continue

        elif line.startswith('PRIMARY KEY'):
            continue

        elif line.startswith('DROP'):
            append(cleanup_stmt(line))

        elif line.startswith('CREATE TABLE'):
            append(cleanup_stmt(line))
            active_table = line.split('`')[1]

        elif line.startswith('KEY'):
            column = line.split('`')[1]
            indexes.append(f'DROP INDEX IF EXISTS [idx_{active_table}_{column}];')
            indexes.append(f"CREATE INDEX IF NOT EXISTS [idx_{active_table}_{column}] ON [{active_table}]([{column}]);")

        elif ';' in line and active_table:

            append('\t' + ',\n\t'.join(columns))

            append(');\n')
            
            for index in indexes:
                append(index)
            
            active_table = False
            indexes = []
            columns = []

            append('')

        elif line.startswith('INSERT'):
            append(cleanup_stmt(line.replace(r'\\n', r'\n')))
            append('')

        else:
            columns.append(cleanup(line.replace(',', '')))
