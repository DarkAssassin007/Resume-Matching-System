"""
Database module for Resume Matching System
Handles SQLite database operations for resumes, job descriptions, and matching results
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = 'data/resume_matching.db'):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Create database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create resumes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_name TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_content TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create job_descriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT NOT NULL,
                description TEXT NOT NULL,
                required_skills TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create matching_results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matching_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                matching_score REAL NOT NULL,
                matched_skills TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes(id),
                FOREIGN KEY (job_id) REFERENCES job_descriptions(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_resume(self, candidate_name: str, file_name: str, file_content: str) -> int:
        """Add a new resume to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO resumes (candidate_name, file_name, file_content)
                VALUES (?, ?, ?)
            ''', (candidate_name, file_name, file_content))
            
            resume_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return int(resume_id) if resume_id else 0
        except Exception as e:
            print(f"Error adding resume to database: {str(e)}")
            # Try to close connection if it's still open
            try:
                conn.close()
            except:
                pass
            return 0
    
    def add_job_description(self, job_title: str, description: str, required_skills: str) -> int:
        """Add a new job description to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO job_descriptions (job_title, description, required_skills)
                VALUES (?, ?, ?)
            ''', (job_title, description, required_skills))
            
            job_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return int(job_id) if job_id else 0
        except Exception as e:
            print(f"Error adding job description to database: {str(e)}")
            # Try to close connection if it's still open
            try:
                conn.close()
            except:
                pass
            return 0
    
    def add_matching_result(self, resume_id: int, job_id: int, matching_score: float, matched_skills: str):
        """Add matching result to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO matching_results (resume_id, job_id, matching_score, matched_skills)
                VALUES (?, ?, ?, ?)
            ''', (resume_id, job_id, matching_score, matched_skills))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error adding matching result to database: {str(e)}")
            # Try to close connection if it's still open
            try:
                conn.close()
            except:
                pass
    
    def get_all_resumes(self) -> List[Dict]:
        """Get all resumes from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resumes ORDER BY created_at DESC')
        resumes = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return resumes
    
    def get_all_job_descriptions(self) -> List[Dict]:
        """Get all job descriptions from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM job_descriptions ORDER BY created_at DESC')
        jobs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return jobs
    
    def get_matching_results(self, job_id: int, limit: int = 10) -> List[Dict]:
        """Get top matching results for a job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                mr.id,
                mr.matching_score,
                mr.matched_skills,
                mr.created_at,
                r.candidate_name,
                r.file_name,
                j.job_title
            FROM matching_results mr
            JOIN resumes r ON mr.resume_id = r.id
            JOIN job_descriptions j ON mr.job_id = j.id
            WHERE mr.job_id = ?
            ORDER BY mr.matching_score DESC
            LIMIT ?
        ''', (job_id, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_resume_by_id(self, resume_id: int) -> Optional[Dict]:
        """Get a specific resume by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        result = cursor.fetchone()
        
        conn.close()
        return dict(result) if result else None
    
    def get_job_by_id(self, job_id: int) -> Optional[Dict]:
        """Get a specific job description by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM job_descriptions WHERE id = ?', (job_id,))
        result = cursor.fetchone()
        
        conn.close()
        return dict(result) if result else None
    
    def clear_matching_results(self, job_id: int):
        """Clear previous matching results for a job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM matching_results WHERE job_id = ?', (job_id,))
        
        conn.commit()
        conn.close()
    
    def delete_resume(self, resume_id: int) -> bool:
        """Delete a resume by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete matching results first (foreign key constraint)
            cursor.execute('DELETE FROM matching_results WHERE resume_id = ?', (resume_id,))
            
            # Delete the resume
            cursor.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting resume: {str(e)}")
            try:
                conn.close()
            except:
                pass
            return False