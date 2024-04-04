import sqlite3
import mysql.connector
import json
import re
# Connect to SQLite database
import sqlite3
import mysql.connector
import os
proxy = 'http://127.0.0.1:8080'
os.environ['http_proxy'] = proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy
os.environ['REQUESTS_CA_BUNDLE'] = "C:\\Users\\User\\Desktop\\cacert.pem"


# Connect to MySQL database
mysql_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="library"
)
mysql_cursor = mysql_connection.cursor()

# Fetch titles of books where cupboard_id=1 from SQLite database
mysql_cursor.execute("SELECT id ,isbn, title, author, publisher,cupboard_id, manual_added,row_id,no_of_copies FROM books1 where  destination_row_id is Null and cupboard_id not in (8,9)")
books_data = mysql_cursor.fetchall()

# Function to determine category
def determine_category(title):


  # Execute the query
  mysql_cursor.execute("SELECT category FROM Row where cupboard_id not in (8,9)")

  # Fetch the result into a list of tuples
  categories = mysql_cursor.fetchall()
  print()

  import requests
  url_chat = 'https://www.blackbox.ai/api/chat'

  payload = {
    "messages": [
      {
        "id": "6ZUkhHE",
        "content": title[:20] + " beongs which categoriy choose one  from following categories [" + str(categories) + "]  reply answer in json format like {\"category\":vaule}",
        # Assuming response is JSON, adjust accordingly
        "role": "user"
      }
    ],
    "id": "6ZUkhHE",
    "previewToken": None,
    "userId": "64ef24a9a502c400325b1793",
    "codeModelMode": False,
    "agentMode": {},
    "trendingAgentMode": {},
    "isMicMode": False,
    "isChromeExt": False,
    "githubToken": None
  }
  headers_upload = {
    'Cookie': 'sessionId=5f3805d8-1238-4010-b57b-87f9a3ea5cf3; personalId=5f3805d8-1238-4010-b57b-87f9a3ea5cf3; intercom-id-jlmqxicb=67d82bf6-f448-43f7-bd52-dc345577e262; intercom-device-id-jlmqxicb=76ad4a43-c19c-4cb3-9cb9-48290974cd7b; __Host-next-auth.csrf-token=ba01088d61dc7aa179bcb0fa3000336e2188c8f790ef22877fc1e42ee5bde16b%7C777a6aa383f028a9e62a4f5a60d1d74fab5c74b80e749c2e8979eb0a0a046be2; __Secure-next-auth.callback-url=https%3A%2F%2Fwww.blackbox.ai%2F; __Secure-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..-YGdOSrxKaLEK80j.bw6VjMZQ_RAX7MiNaovJ2uAwIQz-O9KeqYpeAvWASGTBNDq3Mt23CzAZIETDIWQLchcsdfj13UEkzyZH8JOPGFjByi9c7xrnzYx_M1VC39CLfypqROxihePqZCTqDdfCcyBA9pnlx18iO3Re-SN8I824Fh9LPOiap_TIqIT-lyA0XjHI7mJBD103R0My-nnSCZx-g-zdURyF7P3-r6wNZHl5HC9-JAMG2y8OCnuXRfUIUrE_lapvPxdz0R-R9UaCtGoPqsLPU1jZEHrH7nsWkm-_INgCY6ObU7sqeSHAwIAL2_dVH4CMNA-H_GoNkPBWbAkpvIcEQXmOV6iKiyH3B3o-iHpDgTgHW603L8SrVeZd7XND1EqHzB-kPwQzjPVf53O27IkPQ6vuJaC1oVpppxSd0mNQX7Fx3WaTTE_JyH-REm9NTQ_ZnoKExh0O_s-rYR-LaznTSrXVsrGPABnhBWsGr6C6rT7Jz7W9.YoyOWLcFoVnmoyOTENNbyg; intercom-session-jlmqxicb=UThUbTlkZndVaTQyMFcyTi9mS1J0YzU5NWV4ek16Z2NPNUt5MmlkRHRLUzBTN3lhRjlWWFkwV0N0bWhTdzhmZS0tVTZOd2hYNG9hcFdqeHkxaElJd1RxUT09--44438bcfc4e04cf1dda30b3cfb0abf6c133cf324',
    'Sec-Ch-Ua': '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Ch-Ua-Mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Sec-Gpc': '1',
    'Origin': 'https://www.blackbox.ai',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.blackbox.ai/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9'
  }
  headers_chat = {
    'Cookie': headers_upload['Cookie'],  # Reuse cookie from the first request
    'Sec-Ch-Ua': headers_upload['Sec-Ch-Ua'],
    'Sec-Ch-Ua-Platform': headers_upload['Sec-Ch-Ua-Platform'],
    'Sec-Ch-Ua-Mobile': headers_upload['Sec-Ch-Ua-Mobile'],
    'User-Agent': headers_upload['User-Agent'],
    'Content-Type': 'application/json',
    'Accept': headers_upload['Accept'],
    'Sec-Gpc': headers_upload['Sec-Gpc'],
    'Origin': headers_upload['Origin'],
    'Sec-Fetch-Site': headers_upload['Sec-Fetch-Site'],
    'Sec-Fetch-Mode': headers_upload['Sec-Fetch-Mode'],
    'Sec-Fetch-Dest': headers_upload['Sec-Fetch-Dest'],
    'Referer': headers_upload['Referer'],
    'Accept-Encoding': headers_upload['Accept-Encoding'],
    'Accept-Language': headers_upload['Accept-Language']
  }

  response_chat = requests.post(url_chat, data=json.dumps(payload), headers=headers_chat)

  # Ensure the chat request was successful
  if response_chat.status_code != 200:
    print("Error with chat request:", response_chat.status_code)


  # Extract JSON data from chat response
  json_pattern = r'{(?:[^{}]|{(?:[^{}]|{[^{}]})})*}'

  json_match = re.search(json_pattern, response_chat.text)

  if json_match:
    # Extract the JSON string
    json_string = json_match.group(0)
    print(json_string)

    # Parse the JSON string
    try:
      chat_data = json.loads(json_string)
      cate = chat_data.get('category')


      print("Title:", title)
      print("Category:", cate)
      return cate
    except json.JSONDecodeError as e:
      print("Error decoding JSON:", e)
      return None


  else:
    print("No JSON found in the response string.")
    return None


# Insert data into MySQL database
for book in books_data:

    id, isbn, title, author, publisher, cupboard_id, manual_added, row_id, no_of_copies = book
    if 1:
      print(title)
      category = determine_category(title)
      if category:

          # Insert data into MySQL books table
          sql_query = "UPDATE books1 SET category = %s WHERE id = %s"

          # Specify the values to be substituted into the query
          values = (category, id)

          # Execute the SQL query with placeholders
          mysql_cursor.execute(sql_query, values)

          # Commit the transaction
          mysql_connection.commit()
      else:
            print("error ",id)
            with open("failed.txt", "a") as file:
              file.write(f"{id ,isbn}\n")

# Close connections

mysql_connection.close()
