"""
Migration script to add end_date column to doctor_unavailable table
Run this to add support for leave date ranges
"""
from sqlalchemy import create_engine, Column, Date, text
from sqlalchemy.orm import sessionmaker
from .config import get_settings
import sys

settings = get_settings()

# Create engine
engine = create_engine(settings.database_url)

def add_end_date_column():
    """Add end_date column to doctor_unavailable table"""
    try:
        with engine.connect() as conn:
            # Check if column already exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='doctor_unavailable' AND column_name='end_date';
            """)
            result = conn.execute(check_query)
            
            if result.fetchone():
                print("[OK] Column 'end_date' already exists in doctor_unavailable table")
                return
            
            # Add the column
            alter_query = text("""
                ALTER TABLE doctor_unavailable 
                ADD COLUMN end_date DATE NULL;
            """)
            conn.execute(alter_query)
            conn.commit()
            
            print("[OK] Successfully added 'end_date' column to doctor_unavailable table")
            print("     Doctors can now be marked unavailable for date ranges")
            
    except Exception as e:
        print(f"[ERROR] Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("[INFO] Running migration: Add end_date column to doctor_unavailable table...")
    add_end_date_column()
    print("[OK] Migration complete!")

