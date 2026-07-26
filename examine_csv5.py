import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Scholarships.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)
    
    header_index = 3
    contents_index = 15
    
    print('Sample contents from data rows:')
    for i in range(header_index + 1, min(header_index + 10, len(rows))):
        if len(rows[i]) > contents_index:
            content = rows[i][contents_index]
            print('Row', i, ':', repr(content))
        else:
            print('Row', i, ': Not enough columns')

