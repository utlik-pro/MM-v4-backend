#!/usr/bin/env python3
"""
Vacancy Processing Workflow
Handles the complete workflow for processing job vacancies from creation to posting.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VacancyProcessor:
    def __init__(self, db_path: str = "../database/contacts.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize database tables for vacancy processing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create vacancies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                requirements TEXT,
                salary_range TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                posted_at TIMESTAMP,
                linkedin_url TEXT,
                performance_metrics TEXT
            )
        ''')
        
        # Create applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vacancy_id INTEGER,
                applicant_name TEXT NOT NULL,
                applicant_email TEXT NOT NULL,
                resume_url TEXT,
                cover_letter TEXT,
                status TEXT DEFAULT 'received',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vacancy_id) REFERENCES vacancies (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_vacancy(self, vacancy_data: Dict) -> int:
        """Create a new vacancy record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO vacancies (title, company, location, requirements, salary_range)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            vacancy_data['title'],
            vacancy_data['company'],
            vacancy_data['location'],
            vacancy_data.get('requirements', ''),
            vacancy_data.get('salary_range', '')
        ))
        
        vacancy_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created vacancy: {vacancy_data['title']} (ID: {vacancy_id})")
        return vacancy_id
    
    def generate_job_description(self, vacancy_data: Dict) -> str:
        """Generate optimized job description using AI."""
        # This would integrate with Claude AI for content generation
        template = f"""
# {vacancy_data['title']}
**Company:** {vacancy_data['company']}
**Location:** {vacancy_data['location']}

## About the Role
We are seeking a talented {vacancy_data['title']} to join our team at {vacancy_data['company']}.

## Requirements
{vacancy_data.get('requirements', 'To be specified')}

## Benefits
- Competitive salary
- Health insurance
- Professional development opportunities
- Flexible work arrangements

## How to Apply
Please submit your resume and cover letter through our application portal.

---
*Posted on LinkedIn - {datetime.now().strftime('%Y-%m-%d')}*
        """
        return template.strip()
    
    def post_to_linkedin(self, vacancy_id: int, linkedin_email: str = None, linkedin_password: str = None) -> Dict:
        """Post vacancy to LinkedIn using browser automation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get vacancy data
        cursor.execute('SELECT * FROM vacancies WHERE id = ?', (vacancy_id,))
        vacancy = cursor.fetchone()
        
        if not vacancy:
            raise ValueError(f"Vacancy with ID {vacancy_id} not found")
        
        # Generate job description
        vacancy_data = {
            'id': vacancy_id,
            'title': vacancy[1],
            'company': vacancy[2],
            'location': vacancy[3],
            'requirements': vacancy[4],
            'salary_range': vacancy[5]
        }
        
        # Use browser automation for LinkedIn posting
        try:
            from linkedin_browser_automation import LinkedInBrowserAutomation
            
            # Initialize browser automation
            linkedin_automation = LinkedInBrowserAutomation(headless=False)
            
            # Get LinkedIn credentials from environment or parameters
            if not linkedin_email:
                import os
                linkedin_email = os.getenv('LINKEDIN_EMAIL')
                linkedin_password = os.getenv('LINKEDIN_PASSWORD')
            
            if not linkedin_email or not linkedin_password:
                raise ValueError("LinkedIn credentials not provided")
            
            # Post job using browser automation
            result = linkedin_automation.post_job_vacancy(vacancy_data, linkedin_email, linkedin_password)
            
            if result['success']:
                linkedin_url = result['job_url']
                
                # Update vacancy status
                cursor.execute('''
                    UPDATE vacancies 
                    SET status = 'posted', posted_at = CURRENT_TIMESTAMP, linkedin_url = ?
                    WHERE id = ?
                ''', (linkedin_url, vacancy_id))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Posted vacancy to LinkedIn: {linkedin_url}")
                
                return {
                    'vacancy_id': vacancy_id,
                    'linkedin_url': linkedin_url,
                    'job_description': result.get('job_description', ''),
                    'posted_at': result['posted_at'],
                    'post_id': result['post_id']
                }
            else:
                raise Exception(f"LinkedIn posting failed: {result['error']}")
                
        except ImportError:
            logger.warning("LinkedIn browser automation not available, using simulation")
            # Fallback to simulation
            job_description = self.generate_job_description(vacancy_data)
            linkedin_url = f"https://linkedin.com/jobs/view/{vacancy_id}"
            
            # Update vacancy status
            cursor.execute('''
                UPDATE vacancies 
                SET status = 'posted', posted_at = CURRENT_TIMESTAMP, linkedin_url = ?
                WHERE id = ?
            ''', (linkedin_url, vacancy_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Simulated LinkedIn posting: {linkedin_url}")
            
            return {
                'vacancy_id': vacancy_id,
                'linkedin_url': linkedin_url,
                'job_description': job_description,
                'posted_at': datetime.now().isoformat()
            }
    
    def track_performance(self, vacancy_id: int) -> Dict:
        """Track LinkedIn post performance metrics."""
        # Simulate performance tracking (replace with actual LinkedIn API)
        metrics = {
            'views': 150,
            'applications': 12,
            'shares': 8,
            'engagement_rate': 0.08,
            'quality_score': 0.85
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE vacancies 
            SET performance_metrics = ?
            WHERE id = ?
        ''', (json.dumps(metrics), vacancy_id))
        
        conn.commit()
        conn.close()
        
        return metrics
    
    def process_applications(self, vacancy_id: int) -> List[Dict]:
        """Process applications for a specific vacancy."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM applications 
            WHERE vacancy_id = ? 
            ORDER BY applied_at DESC
        ''', (vacancy_id,))
        
        applications = []
        for row in cursor.fetchall():
            applications.append({
                'id': row[0],
                'applicant_name': row[2],
                'applicant_email': row[3],
                'resume_url': row[4],
                'cover_letter': row[5],
                'status': row[6],
                'applied_at': row[7]
            })
        
        conn.close()
        return applications
    
    def get_vacancy_summary(self, vacancy_id: int) -> Dict:
        """Get comprehensive summary of a vacancy."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get vacancy details
        cursor.execute('SELECT * FROM vacancies WHERE id = ?', (vacancy_id,))
        vacancy = cursor.fetchone()
        
        if not vacancy:
            raise ValueError(f"Vacancy with ID {vacancy_id} not found")
        
        # Get application count
        cursor.execute('SELECT COUNT(*) FROM applications WHERE vacancy_id = ?', (vacancy_id,))
        application_count = cursor.fetchone()[0]
        
        # Get performance metrics
        performance_metrics = json.loads(vacancy[10]) if vacancy[10] else {}
        
        conn.close()
        
        return {
            'id': vacancy[0],
            'title': vacancy[1],
            'company': vacancy[2],
            'location': vacancy[3],
            'requirements': vacancy[4],
            'salary_range': vacancy[5],
            'status': vacancy[6],
            'created_at': vacancy[7],
            'posted_at': vacancy[8],
            'linkedin_url': vacancy[9],
            'application_count': application_count,
            'performance_metrics': performance_metrics
        }

def main():
    """Main workflow execution."""
    processor = VacancyProcessor()
    
    # Example workflow
    vacancy_data = {
        'title': 'Senior Python Developer',
        'company': 'TechCorp',
        'location': 'San Francisco, CA',
        'requirements': 'Python, Django, React, 5+ years experience',
        'salary_range': '$120k-180k'
    }
    
    # Create vacancy
    vacancy_id = processor.create_vacancy(vacancy_data)
    
    # Post to LinkedIn
    posting_result = processor.post_to_linkedin(vacancy_id)
    print(f"Posted vacancy: {posting_result}")
    
    # Track performance
    metrics = processor.track_performance(vacancy_id)
    print(f"Performance metrics: {metrics}")
    
    # Get summary
    summary = processor.get_vacancy_summary(vacancy_id)
    print(f"Vacancy summary: {summary}")

if __name__ == "__main__":
    main() 