import pandas as pd

# Load the CSV
df = pd.read_csv(r'C:\Users\chase\My Drive\Rosters etc\TTH 8-920  CA 4201\Import file.csv')

# Test name matching
student_name = 'Lilli Broussard'
name_parts = student_name.split()
first_name = name_parts[0].lower()
last_name = ' '.join(name_parts[1:]).lower()

print(f'Looking for: {first_name} {last_name}')
print(f'CSV has: {df["First Name"].iloc[1]} {df["Last Name"].iloc[1]}')

# Test the matching logic
mask = (df['First Name'].str.lower().str.contains(first_name, na=False)) & \
       (df['Last Name'].str.lower().str.contains(last_name, na=False))

print(f'Match found: {mask.any()}')
print(f'Matched rows: {mask.sum()}')

if mask.any():
    print('Matched names:')
    print(df.loc[mask, ['First Name', 'Last Name']].to_string())
else:
    print('No matches found')
    print('First 5 names in CSV:')
    print(df[['First Name', 'Last Name']].head().to_string())
