import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import openpyxl

def get_book_info(isbn, filename):
    url = f"https://isbndb.com/book/{isbn}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        # Replace the following values with your actual cookies
        "Cookie": "SESSab6de86aea7caa3f48ba6097cf7cdcf6=WQfvDlz4n%2C9A1hcGBzM21vxIjDj7dnmMRSQeHQklwI%2CVqyN3; __stripe_mid=a8575b27-a8a9-4b95-bbf7-b5469f708e3e4b0442; __stripe_sid=bd3a85fc-9d1a-418f-9e57-f3237afd57ba677f56; AWSALB=+Ml2V0jg9/OwLILg8H6ix/5feWLt3dVR106L5II9XzU91FFyJmE+B1zIm8chmz5J04RFiY1H0LK+akGlm30DdozMciU7AI/SrFx4U79o4LhaB4SoVn66qWs5B1Rz; AWSALBCORS=+Ml2V0jg9/OwLILg8H6ix/5feWLt3dVR106L5II9XzU91FFyJmE+B1zIm8chmz5J04RFiY1H0LK+akGlm30DdozMciU7AI/SrFx4U79o4LhaB4SoVn66qWs5B1Rz"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', class_='book-title').text.strip()
        author_elem = soup.find('th', text='Authors:')
        author = author_elem.find_next_sibling('td').text.strip() if author_elem else "Unknown"
        publisher_elem = soup.find('th', text='Publisher')
        publisher = publisher_elem.find_next_sibling('td').text.strip() if publisher_elem else "Unknown"
        return {'ISBN': isbn, 'Title': title, 'Author': author, 'Publisher': publisher, 'ROW': filename}
    else:
        return None

# Read ISBNs from multiple files and count duplicates
cupboard=input("enter cupboard no")
file_pattern = "cup7/isbn.txt"  # Modify this pattern according to your file naming convention
isbn_counts = {}

for filename in os.listdir('.'):
    if filename.endswith('.txt') and filename != 'books.xlsx':
        print(f"Processing file: {filename}")
        with open(filename, 'r') as file:
            isbns = file.readlines()
            isbns = [isbn.strip() for isbn in isbns]

        for isbn in isbns:
            if isbn in isbn_counts:
                isbn_counts[isbn].append(filename)
            else:
                isbn_counts[isbn] = [filename]
        print(f"ISBNs found in {filename}: {len(isbns)}")

# Create a DataFrame to store book information
book_data = []
for isbn, filenames in isbn_counts.items():
    count = len(filenames)
    for filename in filenames:
        try:
            print(f"Retrieving details for ISBN {isbn} from {filename}")
            book_info = get_book_info(isbn, filename)
            if book_info:
                book_info['Number of Copies'] = count
                book_data.append(book_info)
                print(f"Details retrieved for ISBN {isbn} from {filename}")
        except Exception as e:
                # Code to handle the exception
                with open("cup7/failed.txt", "a") as file:
                    file.write(f"{isbn}\n")
                    continue

# Create DataFrame
df = pd.DataFrame(book_data)

# Save to Excel
excel_file = cupboard+".xlsx"
df.to_excel(excel_file, index=False)
print(f"Data saved to '{excel_file}'")
