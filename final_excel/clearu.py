import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('books.db')
cursor = conn.cursor()

# Execute the DELETE statement
cursor.execute("DELETE FROM Book WHERE title IS NULL OR title = '' OR title = 'Unknown' OR title = 'None'")

# Commit the changes
conn.commit()

# Close the connection
conn.close()