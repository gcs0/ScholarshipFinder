import csv

with open('Scholarships.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)
    
    print('Total rows:', len(rows))
    print('Columns per row:', [len(row) for row in rows[:5]])
    print('\nFirst 3 rows:')
    for i, row in enumerate(rows[:3]):
        print(f'Row {i}: {len(row)} columns')
        for j, col in enumerate(row[:5]):  # First 5 columns
            print(f'  Col {j}: {col[:50]}...' if len(col) > 50 else f'  Col {j}: {col}')

