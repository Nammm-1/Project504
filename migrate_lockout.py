"""
Database migration script to add account lockout fields to the User table.
"""
import psycopg2
from psycopg2 import sql
import os

def run_lockout_migration():
    """
    Run database migration to add account lockout fields to the User table
    """
    print("Starting migration to add account lockout fields to User table...")
    
    # Get database connection string from environment
    database_url = os.environ.get('DATABASE_URL')
    
    try:
        # Connect directly using psycopg2 to avoid SQLAlchemy conflicts
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
    # Run the migration when script is executed directly
    success = run_lockout_migration()
    print(f"Migration {'succeeded' if success else 'failed'}.")