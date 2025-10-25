<<<<<<< HEAD

=======
import sqlite3

conn = sqlite3.connect("delivery_tracker.db")

cursor = conn.cursor()

def main():
    query = cursor.execute("SELECT * FROM business_unit;")

    results = query.fetchall()

    for result in results:
        print(results)

if __name__ == '__main__':
       main()
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
