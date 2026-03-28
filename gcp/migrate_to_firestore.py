#!/usr/bin/env python3
"""
Migration script to convert local CSV/YAML data to Firestore
Run this before going live to preserve existing student and attendance data
"""

import os
import csv
import sys
import json
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from firestore_service import save_student_embedding, log_attendance
except ImportError:
    print("ERROR: Could not import firestore_service")
    print("Make sure you're in the project root and backend is in PYTHONPATH")
    sys.exit(1)

def migrate_students():
    """Migrate students from StudentDetails/studentdetails.csv to Firestore"""
    csv_path = Path(__file__).parent.parent / "StudentDetails" / "studentdetails.csv"
    
    if not csv_path.exists():
        print(f"⚠️  No student CSV found at {csv_path}")
        return 0
    
    print(f"\n📚 Migrating students from {csv_path}...")
    count = 0
    
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            
            for row in reader:
                if len(row) < 2:
                    continue
                
                student_id = row[0].strip()
                name = row[1].strip()
                
                # Create placeholder embedding (all zeros)
                embedding = [0.0] * 512
                
                success = save_student_embedding(student_id, name, embedding)
                if success:
                    print(f"  ✓ {student_id}: {name}")
                    count += 1
                else:
                    print(f"  ✗ {student_id}: {name} (FAILED)")
        
        print(f"\n✅ Migrated {count} students to Firestore")
        return count
    
    except Exception as e:
        print(f"❌ Error during student migration: {e}")
        return 0

def migrate_attendance():
    """Migrate attendance records from CSV files to Firestore"""
    attendance_dir = Path(__file__).parent.parent / "Attendance"
    
    if not attendance_dir.exists():
        print(f"⚠️  No attendance directory found at {attendance_dir}")
        return 0
    
    print(f"\n📋 Migrating attendance records from {attendance_dir}...")
    count = 0
    
    try:
        for csv_file in attendance_dir.rglob("*.csv"):
            subject = csv_file.stem.split('_')[0]
            print(f"  Processing: {csv_file.name} (subject: {subject})")
            
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                
                for row in reader:
                    if len(row) < 2:
                        continue
                    
                    student_id = row[0].strip()
                    student_name = row[1].strip() if len(row) > 1 else f"Student_{student_id}"
                    
                    success = log_attendance(student_id, student_name, subject)
                    if success:
                        count += 1
        
        print(f"\n✅ Migrated {count} attendance records to Firestore")
        return count
    
    except Exception as e:
        print(f"❌ Error during attendance migration: {e}")
        return 0

def verify_migration():
    """Verify that migration was successful"""
    from firestore_service import get_all_students, get_attendance_records
    
    print("\n🔍 Verifying migration...")
    
    try:
        students = get_all_students()
        print(f"  ✓ Found {len(students)} students in Firestore")
        
        attendance = get_attendance_records()
        print(f"  ✓ Found {len(attendance)} attendance records in Firestore")
        
        print("\n✅ Migration verification complete!")
        return True
    
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    print("=" * 50)
    print("Firestore Migration Script")
    print("=" * 50)
    
    print("\n⚠️  This script will migrate local CSV data to Firestore")
    print("📍 Make sure FIRESTORE_PROJECT_ID env var is set")
    print("📍 Ensure firestore_service.py is properly initialized\n")
    
    # Check environment
    project_id = os.getenv("FIRESTORE_PROJECT_ID")
    if not project_id:
        print("❌ ERROR: FIRESTORE_PROJECT_ID not set")
        print("Set with: export FIRESTORE_PROJECT_ID=your-project-id")
        sys.exit(1)
    
    print(f"✓ Using project: {project_id}\n")
    
    confirm = input("Continue with migration? (yes/no): ").lower()
    if confirm != 'yes':
        print("Migration cancelled")
        sys.exit(0)
    
    # Run migrations
    student_count = migrate_students()
    attendance_count = migrate_attendance()
    
    # Verify
    verify_migration()
    
    print("\n" + "=" * 50)
    print("Migration Summary")
    print("=" * 50)
    print(f"Students migrated: {student_count}")
    print(f"Attendance records migrated: {attendance_count}")
    print(f"Total records: {student_count + attendance_count}")
    print("\n✅ Migration complete! Data is now in Firestore")

if __name__ == "__main__":
    main()
