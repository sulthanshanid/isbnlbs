import re
import requests
import cv2
import numpy as np
import os
import argparse
import platform
import pathlib
import time
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from pytesseract import Output
import pytesseract

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Directory to store uploaded files


# Image processing functions
def get_grayscale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.bitwise_not(gray)


def rotate(image, rotate_angle, center=None, scale=1.0):
    angle = 360 - rotate_angle
    (h, w) = image.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated


def find_isbn(data):
    regex_pattern = r'(ISBN[-:]*(1[03])*[ ]*(: ){0,1})*(([0-9Xx][- \'"]*){13}|([0-9Xx][- \'"]*){10})'
    x = re.search(regex_pattern, data)

    if x:
        data = re.sub('[ISBN^(: )]+', '', x.group())
        removed_dash = data.replace('-', '')
        remove_others = removed_dash.replace('"', '')
        return remove_others
    else:
        return None


def get_book_info(isbn):
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
        title_element = soup.find('h1', class_='book-title')
        title = title_element.text.strip() if title_element else "Unknown"
        author_elem = soup.find('th', text='Authors:')
        author = author_elem.find_next_sibling('td').text.strip() if author_elem else "Unknown"
        publisher_elem = soup.find('th', text='Publisher')
        publisher = publisher_elem.find_next_sibling('td').text.strip() if publisher_elem else "Unknown"
        return {'ISBN': isbn, 'Title': title, 'Author': author, 'Publisher': publisher}
    else:
        return None


# Main function
def scan_image(file):
    image = cv2.imread(file)
    image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    angle_list = [90, 180, 270, 360]

    try:
        for angle in angle_list:
            rotate_image = rotate(image=image, rotate_angle=angle)
            gray = get_grayscale(image=rotate_image)
            data = pytesseract.image_to_string(gray, config='')
            isbn_value = find_isbn(data)
            if isbn_value:
                return isbn_value
    except Exception as e:
        print("Error occurred:", e)
    return None


@app.route('/')
def index():
    return render_template('isbntext.html')


@app.route('/isbntext', methods=['POST'])
def isbntext():
    data = request.json
    isbn = data.get('isbn')
    if not isbn:
        return jsonify({'error': 'ISBN number not provided'})

    book_info = get_book_info(isbn)
    if book_info:
        return jsonify(book_info)
    else:
        return jsonify({'error': 'Book details not found'})


@app.route('/manual', methods=['POST'])
def extract_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filename = secure_filename(file.filename)  # Extract filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save file

    try:
        isbn = scan_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Process image
        if isbn:
            book_info = get_book_info(isbn)
            if book_info:
                return jsonify(book_info)
            else:
                return jsonify({'error': 'Book details not found'})
        else:
            return jsonify({'error': "No ISBN FOUND"})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/manual1', methods=['POST'])
def test():
  title = None
  author = None
  publisher = None
  try:
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filename = secure_filename(file.filename)  # Extract filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # Second Method: Use API to extract data
    import requests
    import json
    import re

    # First Request - Upload Image
    url_upload = 'https://www.blackbox.ai/api/upload'
    files = {'image': open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb')}
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
    response_upload = requests.post(url_upload, files=files, headers=headers_upload)

    # Ensure the upload was successful
    if response_upload.status_code != 200:
        print("Error uploading image:", response_upload.status_code)
        exit()

    # Convert the response content from bytes to string
    response_content_str = response_upload.content.decode('utf-8')

    # Second Request - Chat API with First Response
    url_chat = 'https://www.blackbox.ai/api/chat'

    payload = {
        "messages": [
            {
                "id": "6ZUkhHE",
                "content": response_content_str + "give me answer in json format extract title ,author,publisher ",
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
        exit()

    # Extract JSON data from chat response
    json_pattern = r'{(?:[^{}]|{(?:[^{}]|{[^{}]})})*}'

    json_match = re.search(json_pattern, response_chat.text)

    if json_match:
        # Extract the JSON string
        json_string = json_match.group(0)

        # Parse the JSON string
        try:
            chat_data = json.loads(json_string)
            title = chat_data.get('title')
            authors = chat_data.get('author')
            if authors:
                if isinstance(authors, list):
                    author = authors[0]  # Select the first author if available
                else:
                    # Split the string of authors by commas and take the first author
                    author = authors.split(',')[0].strip()
            else:
                author = "Unknown"  # Set a default value if no author is provided
            publisher = chat_data.get('publisher')
            print("Title:", title)
            print("Author:", author)
            print("Publisher:", publisher)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)


    else:
        print("No JSON found in the response string.")

    # Third Request - OpenLibrary Search
    url_search = f"https://openlibrary.org/search?q={title}+{author}"
    headers_search = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    response_search = requests.get(url_search, headers=headers_search)

    if response_search.status_code == 200:
        response_json = json.loads(response_search.content)

        # Extract ISBNs
        isbn_list = []
        for doc in response_json['docs']:
            if 'isbn' in doc:
                isbn_list.extend(doc['isbn'])

        # If no ISBNs found, set ISBN to None
        if not isbn_list:
            isbn = None
        else:
            # Get the first ISBN
            isbn = isbn_list[0]

        # Print the ISBN if available
        if isbn:
            print("ISBN:", isbn)
            #book=get_book_info(isbn)
        # Return book information
        return {'ISBN': isbn, 'Title': title, 'Author': author, 'Publisher': publisher}

    else:
        print("Error:", response_search.status_code)



  except Exception as e:
      return jsonify({'error': str(e)})
  return jsonify({'error': 'Unexpected error occurred'})
@app.route('/extract_isbn', methods=['POST'])
def extract_isbn():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filename = secure_filename(file.filename)  # Extract filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save file

    try:
        isbn = scan_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Process image
        if isbn:
            book_info = get_book_info(isbn)
            if book_info:
                return jsonify(book_info)
            else:
                return jsonify({'error': 'Book details not found'})
        else:
            return jsonify({'error': 'No ISBN found in the image'})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='192.168.1.4', port=5000)
