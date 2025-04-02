"""
Database migration script to add account lockout fields to the User table.
Can be run both in Replit and PyCharm environments.
"""
import psycopg2
from psycopg2 import sql
import os
import sys

def run_lockout_migration(custom_db_url=None):
    """
    Run database migration to add account lockout fields to the User table
    
    Args:
        custom_db_url: Optional database URL to use instead of environment variable
    """
    print("Starting migration to add account lockout fields to User table...")
    
    # Get database connection string
    database_url = custom_db_url
    
    # If no custom URL provided, try to get from environment or config file
    if not database_url:
        # Try environment variable first (for Replit)
        database_url = os.environ.get('DATABASE_URL')
        
        # If not in environment, try to load from config.py (for PyCharm)
        if not database_url:
            try:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from config import DATABASE_URL
                database_url = DATABASE_URL
                print(f"Using database URL from config.py")
            except (ImportError, AttributeError):
                print("Could not find DATABASE_URL in environment or config.py")
                return False
    
    try:
        # Connect directly using psycopg2 to avoid SQLAlchemy conflicts
        print(f"Connecting to database...")
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Check if columns exist
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'user'")
        existing_columns = [col[0] for col in cur.fetchall()]
        
        # Add failed_login_attempts column if not present
        if 'failed_login_attempts' not in existing_columns:
            print("Adding failed_login_attempts column...")
            cur.execute(
                sql.SQL("ALTER TABLE {} ADD COLUMN {} INTEGER DEFAULT 0").format(
                    sql.Identifier("user"),
                    sql.Identifier("failed_login_attempts")
                )
            )
            
        # Add lockout_until column if not present
        if 'lockout_until' not in existing_columns:
            print("Adding lockout_until column...")
            cur.execute(
                sql.SQL("ALTER TABLE {} ADD COLUMN {} TIMESTAMP").format(
                    sql.Identifier("user"),
                    sql.Identifier("lockout_until")
                )
            )
            
        conn.commit()
        cur.close()
        conn.close()
        
        print("Migration completed successfully!")
        return True
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Allow passing database URL as command-line argument
    custom_db_url = None
    if len(sys.argv) > 1:
        custom_db_url = sys.argv[1]
        print(f"Using provided database URL from command line")
    
    # Run the migration
    success = run_lockout_migration(custom_db_url)
    print(f"Migration {'succeeded' if success else 'failed'}.")
    
    # Keep console window open in PyCharm
    if not success:
        input("Press Enter to exit...")