import sqlite3
import shutil

def remove_duplicate_title_entries(db_file, new_db_file):
    # Connect to the original SQLite database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Count rows before deletion
    c.execute("SELECT COUNT(*) FROM book")
    before_count = c.fetchone()[0]
    print(f"Before deletion: {before_count} rows")

    # Execute SQL command to delete duplicate entries based on title
    c.execute("""
        DELETE FROM book
        WHERE title IS NOT NULL AND title <> '' AND rowid NOT IN (
            SELECT MIN(rowid)
            FROM book
            WHERE title IS NOT NULL AND title <> ''
            GROUP BY title
        )
    """)

    # Count rows after deletion
    c.execute("SELECT COUNT(*) FROM book")
    after_count = c.fetchone()[0]

    # Commit the changes
    conn.commit()

    # Close the connection to the original database
    conn.close()

    # Copy the modified data to a new database file
    shutil.copyfile(db_file, new_db_file)

    # Print the number of rows found and removed
    print(f"Found {before_count - after_count} duplicate rows and removed them.")

# Replace 'books.db' with the path to your SQLite database file
db_file = 'books.db'
# Replace 'boooook.db' with the desired path and name for the new database file
new_db_file = 'boooook.db'

# Call the function to remove duplicate entries based on title and save as a new database
remove_duplicate_title_entries(db_file, new_db_file)
