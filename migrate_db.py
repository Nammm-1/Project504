import os
from sqlalchemy import create_engine, text
from app import app

def run_migration():
    """
    Run database migration to add 2FA fields to the User table
    """
    print("Starting database migration to add 2FA fields...")
    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("Error: DATABASE_URL environment variable is not set")
        return False
    
    # Create engine
    engine = create_engine(database_url)
    
    try:
        # Execute migration SQL - add OTP columns if they don't exist
        with engine.connect() as conn:
            # Check if columns exist
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'otp_secret'
            """))
            
            if result.fetchone() is None:
                # Add the OTP columns
                print("Adding 2FA columns to the User table...")
                conn.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN IF NOT EXISTS otp_secret VARCHAR(32),
                    ADD COLUMN IF NOT EXISTS otp_enabled BOOLEAN DEFAULT FALSE,
                    ADD COLUMN IF NOT EXISTS otp_verified BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                print("Migration completed successfully!")
            else:
                print("2FA columns already exist - no migration needed.")
                
        return True
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    with app.app_context():
        run_migration()