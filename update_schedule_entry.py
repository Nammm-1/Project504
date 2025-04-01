from app import app, db
from sqlalchemy import text

with app.app_context():
    # Create a temporary schedule_entry table with nullable volunteer_id
    with db.engine.connect() as conn:
        conn.execute(text("ALTER TABLE schedule_entry ALTER COLUMN volunteer_id DROP NOT NULL"))
        conn.commit()
    
    print("Successfully updated schedule_entry table to allow null volunteer_id")

