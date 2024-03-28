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
