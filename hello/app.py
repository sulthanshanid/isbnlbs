import pymysql
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

HOST = 'localhost'
PORT = 3306
DATABASE = 'library'
USER = 'root'
PASSWORD = ''

def connect_to_database():
    return pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE, cursorclass=pymysql.cursors.DictCursor)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/book/<int:book_id>', methods=['GET'])
def get_book(book_id):
    # Connect to the database
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            # Fetch book details by ID
            sql = "SELECT books.*,roww.row_number_inside_cupboard FROM books,roww WHERE book_id = %s and  books.destination_row=roww.id "
            cursor.execute(sql, (book_id,))
            book = cursor.fetchone()
            return jsonify({'book': book}), 200 if book else 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('query')
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            sql_query = """
                SELECT 
                    books.*, 
                    roww.category AS roww_category,
                    roww.row_number_inside_cupboard,
                    cupboard.id AS cupboard_id,
                    CASE
                        WHEN books.barcode IS NOT NULL THEN 'assigned'
                        ELSE 'not_assigned'
                    END AS barcode_status
                FROM 
                    books
                LEFT JOIN 
                    roww ON books.destination_row = roww.id
                LEFT JOIN 
                    cupboard ON roww.cupboard_id = cupboard.id
                WHERE 
                    books.isbn LIKE %s 
                    OR books.title LIKE %s 
                    OR books.barcode LIKE %s
            """
            cursor.execute(sql_query, ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
            books = cursor.fetchall()
            return jsonify({'books': books}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()
@app.route('/add_duplicate', methods=['POST'])
def add_duplicate_book():
    data = request.json
    book_id = data.get('bookID')
    barcode = data.get('barcode')

    if not (book_id and barcode):
        return jsonify({'error': 'Incomplete data provided'}), 400

    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            # Fetch the book details
            cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
            book = cursor.fetchone()
            if not book:
                return jsonify({'error': 'Book not found'}), 404

            # Insert a duplicate of the book with a new barcode
            cursor.execute("""
                INSERT INTO books (isbn, title, author, publisher, added_manually, cupboard_id, destination_row, category_name, copies_available, barcode)
                SELECT isbn, title, author, publisher, added_manually, cupboard_id, destination_row, category_name, copies_available, %s
                FROM books
                WHERE book_id = %s
            """, (barcode, book_id))
            connection.commit()
            return jsonify({'message': 'Duplicate book added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@app.route('/update', methods=['POST'])
def update_book():
    data = request.json
    book_id = data.get('bookID')
    destinationcupboard = data.get('destinationcupboard')
    destinationrow = data.get('destinationrow')
    barcode = data.get('barcode')

    if not (book_id and destinationcupboard and destinationrow and barcode):
        return jsonify({'error': 'Incomplete data provided'}), 400

    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            # Check if barcode already exists
            cursor.execute("SELECT * FROM books WHERE barcode =%s AND book_id != %s", ( barcode,book_id))
            existing_book = cursor.fetchone()
            if existing_book:
                return jsonify({'error': 'Barcode already exists for another book. Consider editing the existing book or choose a different barcode.'}), 400

            # Update book destination and barcode
            sql = """
               UPDATE books
                SET cupboard_id = %s, 
                    destination_row = (SELECT id from roww where row_number_inside_cupboard  = %s and cupboard_id = %s) ,barcode = %s
                WHERE book_id = %s
            """
            cursor.execute(sql, (destinationcupboard, destinationrow, destinationcupboard,barcode, book_id))
            connection.commit()
            return jsonify({'message': 'Book updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
