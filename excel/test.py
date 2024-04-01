import os
import csv
import re

def extract_isbn_from_csv(csv_file):
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        isbn_list = []
        for row in reader:
            for cell in row:
                # Regular expression to match ISBN format (example: 9788120307780)
                isbn_matches = re.findall(r'\b\d{13}\b', cell)
                isbn_list.extend(isbn_matches)
    return isbn_list

def write_isbn_to_txt(isbn_list, output_file):
    with open(output_file, 'w') as file:
        for isbn in isbn_list:
            file.write(isbn + '\n')

# Get the current working directory
current_directory = os.getcwd()

# Extract ISBN numbers from all CSV files in the current directory
csv_files = [filename for filename in os.listdir(current_directory) if filename.endswith('.csv')]

# Dictionary to store ISBNs based on the character after the underscore
isbn_dict = {}

# Group ISBNs by the character after the underscore
for csv_file in csv_files:
    prefix = csv_file.split('_')[1][0]  # Extract the character after the underscore
    csv_path = os.path.join(current_directory, csv_file)
    isbns = extract_isbn_from_csv(csv_path)
    if prefix not in isbn_dict:
        isbn_dict[prefix] = []
    isbn_dict[prefix].extend(isbns)

# Write ISBNs to separate text files based on the character after the underscore
for prefix, isbns in isbn_dict.items():
    output_file = f"{prefix}.txt"
    write_isbn_to_txt(isbns, output_file)
