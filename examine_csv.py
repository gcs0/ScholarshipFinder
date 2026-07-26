import csv

with open('Scholarships.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)[:10]
    
    print('Columns:', rows[0])
    print('\nFirst few contents fields:')
    
    for i, row in enumerate(rows[1:]):
        if len(row) > 13:
            print(f'Row {i+1} Contents: {row[13][:100]}')
        else:
            print(f'Row {i+1} Contents: N/A')

