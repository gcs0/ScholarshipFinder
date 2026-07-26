import csv

with open('Scholarships.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)
    
    # Find the header row
    header_row = None
    header_index = None
    for i, row in enumerate(rows):
        if 'Contents' in ' '.join(row):
            header_row = row
            header_index = i
            break
    
    print('Header row found at index:', header_index)
    print('Header columns:', header_row)
    
    # Find the contents column index
    contents_index = None
    if header_row:
        for i, col in enumerate(header_row):
            if 'Contents' in col:
                contents_index = i
                print(f'Contents column found at index: {i}')
                break
    
    # Show some sample data
    if contents_index is not None and header_index is not None:
        print('\nSample contents from data rows:')
        for i in range(header_index + 1, min(header_index + 5, len(rows))):
            if len(rows[i]) > contents_index:
                print(f'Row {i}: {rows[i][contents_index][:100]}...')
            else:
                print(f'Row {i}: Not enough columns')

