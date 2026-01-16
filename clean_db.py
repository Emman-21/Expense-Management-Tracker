import sqlite3
from datetime import datetime

DB_FILE = 'expenses_tracker.db' 

target_month = datetime.now().strftime("%Y-%m") 

print(f"Checking for old transactions for month: {target_month}")
print("-" * 40)

try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM transactions WHERE month=?", (target_month,))
    count_before = cursor.fetchone()[0]
    
    if count_before > 0:
        cursor.execute("DELETE FROM transactions WHERE month=?", (target_month,))
        conn.commit()
        print(f"🎉 SUCCESS: Deleted {count_before} old categorized transactions for {target_month}.")
        print("You can now run your main app and the total will start from zero.")
    else:
        print("No old categorized transactions found for this month. Database is clean.")

except sqlite3.Error as e:
    print(f"❌ DATABASE ERROR: Could not clear data. Error: {e}")
    
finally:
    if conn:
        conn.close()