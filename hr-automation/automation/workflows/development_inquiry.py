#!/usr/bin/env python3
"""
Development Inquiry Workflow
Handles inquiries from developers and technical candidates.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevelopmentInquiryProcessor:
    def __init__(self, db_path: str = "../database/contacts.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize database tables for development inquiries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create inquiries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS development_inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                inquiry_type TEXT NOT NULL,
                subject TEXT NOT NULL,
                message_content TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                responded_at TIMESTAMP,
                response_content TEXT,
                assigned_to TEXT,
                tags TEXT
            )
        ''')
        
        # Create contacts table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                linkedin_url TEXT,
                github_url TEXT,
                skills TEXT,
                experience_years INTEGER,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_contact TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def process_inquiry(self, inquiry_data: Dict) -> Dict:
        """Process a new development inquiry."""
        # Extract contact information
        contact_info = self.extract_contact_info(inquiry_data)
        
        # Create or update contact
        contact_id = self.upsert_contact(contact_info)
        
        # Analyze inquiry content
        analysis = self.analyze_inquiry(inquiry_data['message'])
        
        # Create inquiry record
        inquiry_id = self.create_inquiry_record(contact_id, inquiry_data, analysis)
        
        # Generate response
        response = self.generate_response(analysis)
        
        # Update inquiry with response
        self.update_inquiry_response(inquiry_id, response)
        
        return {
            'inquiry_id': inquiry_id,
            'contact_id': contact_id,
            'analysis': analysis,
            'response': response,
            'priority': analysis['priority']
        }
    
    def extract_contact_info(self, inquiry_data: Dict) -> Dict:
        """Extract contact information from inquiry."""
        # This would use NLP to extract contact details
        # For now, using simple regex patterns
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\+?[\d\s\-\(\)]{10,}'
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        github_pattern = r'github\.com/[\w\-]+'
        
        message = inquiry_data['message']
        
        contact_info = {
            'name': inquiry_data.get('name', 'Unknown'),
            'email': inquiry_data.get('email', ''),
            'phone': '',
            'linkedin_url': '',
            'github_url': '',
            'skills': '',
            'experience_years': None,
            'location': ''
        }
        
        # Extract email
        emails = re.findall(email_pattern, message)
        if emails and not contact_info['email']:
            contact_info['email'] = emails[0]
        
        # Extract phone
        phones = re.findall(phone_pattern, message)
        if phones:
            contact_info['phone'] = phones[0]
        
        # Extract LinkedIn
        linkedin_matches = re.findall(linkedin_pattern, message)
        if linkedin_matches:
            contact_info['linkedin_url'] = f"https://{linkedin_matches[0]}"
        
        # Extract GitHub
        github_matches = re.findall(github_pattern, message)
        if github_matches:
            contact_info['github_url'] = f"https://{github_matches[0]}"
        
        return contact_info
    
    def analyze_inquiry(self, message: str) -> Dict:
        """Analyze inquiry content for intent and priority."""
        message_lower = message.lower()
        
        # Define keywords for different inquiry types
        keywords = {
            'job_application': ['apply', 'application', 'job', 'position', 'role', 'hire'],
            'project_inquiry': ['project', 'freelance', 'contract', 'collaboration', 'partnership'],
            'technical_question': ['question', 'help', 'advice', 'guidance', 'problem'],
            'networking': ['connect', 'network', 'meet', 'coffee', 'chat'],
            'urgent': ['urgent', 'asap', 'immediate', 'emergency', 'critical']
        }
        
        # Analyze inquiry type
        inquiry_type = 'general'
        max_score = 0
        
        for inquiry_type_name, type_keywords in keywords.items():
            score = sum(1 for keyword in type_keywords if keyword in message_lower)
            if score > max_score:
                max_score = score
                inquiry_type = inquiry_type_name
        
        # Determine priority
        priority = 'medium'
        if any(word in message_lower for word in keywords['urgent']):
            priority = 'high'
        elif inquiry_type == 'job_application':
            priority = 'high'
        elif inquiry_type == 'networking':
            priority = 'low'
        
        # Extract skills mentioned
        skills = self.extract_skills(message)
        
        # Extract experience level
        experience_years = self.extract_experience(message)
        
        return {
            'type': inquiry_type,
            'priority': priority,
            'skills': skills,
            'experience_years': experience_years,
            'sentiment': 'positive',  # Would use sentiment analysis
            'requires_immediate_response': priority == 'high'
        }
    
    def extract_skills(self, message: str) -> List[str]:
        """Extract technical skills from message."""
        # Common programming languages and technologies
        skills_keywords = [
            'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'sql', 'mongodb',
            'redis', 'git', 'linux', 'agile', 'scrum', 'devops', 'ci/cd'
        ]
        
        message_lower = message.lower()
        found_skills = []
        
        for skill in skills_keywords:
            if skill in message_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def extract_experience(self, message: str) -> Optional[int]:
        """Extract years of experience from message."""
        # Look for patterns like "X years", "X+ years", etc.
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*experience',
            r'(\d+)\+?\s*years?\s*in\s*development',
            r'(\d+)\+?\s*years?\s*of\s*coding'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, message.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def upsert_contact(self, contact_info: Dict) -> int:
        """Create or update contact record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if contact exists
        cursor.execute('SELECT id FROM contacts WHERE email = ?', (contact_info['email'],))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing contact
            cursor.execute('''
                UPDATE contacts 
                SET name = ?, phone = ?, linkedin_url = ?, github_url = ?, 
                    skills = ?, experience_years = ?, location = ?, last_contact = CURRENT_TIMESTAMP
                WHERE email = ?
            ''', (
                contact_info['name'], contact_info['phone'], contact_info['linkedin_url'],
                contact_info['github_url'], json.dumps(contact_info['skills']),
                contact_info['experience_years'], contact_info['location'], contact_info['email']
            ))
            contact_id = existing[0]
        else:
            # Create new contact
            cursor.execute('''
                INSERT INTO contacts (name, email, phone, linkedin_url, github_url, skills, experience_years, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contact_info['name'], contact_info['email'], contact_info['phone'],
                contact_info['linkedin_url'], contact_info['github_url'],
                json.dumps(contact_info['skills']), contact_info['experience_years'],
                contact_info['location']
            ))
            contact_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return contact_id
    
    def create_inquiry_record(self, contact_id: int, inquiry_data: Dict, analysis: Dict) -> int:
        """Create a new inquiry record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO development_inquiries (contact_id, inquiry_type, subject, message_content, priority, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            contact_id,
            analysis['type'],
            inquiry_data.get('subject', 'Development Inquiry'),
            inquiry_data['message'],
            analysis['priority'],
            json.dumps(analysis['skills'])
        ))
        
        inquiry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return inquiry_id
    
    def generate_response(self, analysis: Dict) -> str:
        """Generate appropriate response based on inquiry analysis."""
        if analysis['type'] == 'job_application':
            return self.generate_job_application_response(analysis)
        elif analysis['type'] == 'project_inquiry':
            return self.generate_project_response(analysis)
        elif analysis['type'] == 'technical_question':
            return self.generate_technical_response(analysis)
        elif analysis['type'] == 'networking':
            return self.generate_networking_response(analysis)
        else:
            return self.generate_general_response(analysis)
    
    def generate_job_application_response(self, analysis: Dict) -> str:
        """Generate response for job applications."""
        skills_text = ', '.join(analysis['skills']) if analysis['skills'] else 'your background'
        
        response = f"""
Thank you for your interest in joining our team!

We've received your application and are impressed by your experience with {skills_text}. 

Our team will review your application and get back to you within 2-3 business days. In the meantime, feel free to check out our current openings at [company careers page].

If you have any questions, please don't hesitate to reach out.

Best regards,
The HR Team
        """
        return response.strip()
    
    def generate_project_response(self, analysis: Dict) -> str:
        """Generate response for project inquiries."""
        response = f"""
Thank you for reaching out about potential collaboration opportunities!

We're always interested in connecting with talented developers like yourself. While we don't have any immediate project needs, we'd be happy to keep your information on file for future opportunities.

Could you please share your portfolio or recent project examples? This will help us better understand your expertise and reach out when relevant opportunities arise.

Best regards,
The Development Team
        """
        return response.strip()
    
    def generate_technical_response(self, analysis: Dict) -> str:
        """Generate response for technical questions."""
        response = f"""
Thank you for your technical question!

We appreciate you reaching out. While we can't provide detailed technical consultation, we'd be happy to point you to relevant resources or connect you with our technical team if appropriate.

For general technical discussions, we recommend checking out our developer community forums or reaching out to our technical support team.

Best regards,
The Development Team
        """
        return response.strip()
    
    def generate_networking_response(self, analysis: Dict) -> str:
        """Generate response for networking requests."""
        response = f"""
Thank you for reaching out to connect!

We're always happy to network with fellow developers and industry professionals. While we can't accommodate individual coffee meetings at the moment, we'd be happy to connect on LinkedIn and stay in touch for future opportunities.

Feel free to follow our company page for updates on events, job openings, and industry insights.

Best regards,
The Team
        """
        return response.strip()
    
    def generate_general_response(self, analysis: Dict) -> str:
        """Generate general response for other inquiries."""
        response = f"""
Thank you for reaching out!

We've received your inquiry and will get back to you as soon as possible. If this is urgent, please let us know and we'll prioritize your request.

In the meantime, feel free to check out our website for more information about our company and opportunities.

Best regards,
The Team
        """
        return response.strip()
    
    def update_inquiry_response(self, inquiry_id: int, response: str):
        """Update inquiry with generated response."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE development_inquiries 
            SET status = 'responded', responded_at = CURRENT_TIMESTAMP, response_content = ?
            WHERE id = ?
        ''', (response, inquiry_id))
        
        conn.commit()
        conn.close()
    
    def get_inquiry_summary(self, days: int = 7) -> Dict:
        """Get summary of inquiries for the specified period."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get inquiry counts by type
        cursor.execute('''
            SELECT inquiry_type, COUNT(*) as count
            FROM development_inquiries 
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY inquiry_type
        '''.format(days))
        
        type_counts = dict(cursor.fetchall())
        
        # Get priority distribution
        cursor.execute('''
            SELECT priority, COUNT(*) as count
            FROM development_inquiries 
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY priority
        '''.format(days))
        
        priority_counts = dict(cursor.fetchall())
        
        # Get response time metrics
        cursor.execute('''
            SELECT AVG(julianday(responded_at) - julianday(created_at)) as avg_response_days
            FROM development_inquiries 
            WHERE responded_at IS NOT NULL 
            AND created_at >= datetime('now', '-{} days')
        '''.format(days))
        
        avg_response_days = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'period_days': days,
            'total_inquiries': sum(type_counts.values()),
            'inquiry_types': type_counts,
            'priority_distribution': priority_counts,
            'avg_response_days': round(avg_response_days, 2)
        }

def main():
    """Main workflow execution."""
    processor = DevelopmentInquiryProcessor()
    
    # Example inquiry
    inquiry_data = {
        'name': 'John Developer',
        'email': 'john@example.com',
        'subject': 'Job Application - Senior Python Developer',
        'message': '''
        Hi there,
        
        I'm interested in applying for the Senior Python Developer position. 
        I have 5+ years of experience with Python, Django, React, and AWS.
        You can find my portfolio at github.com/johndeveloper and my LinkedIn at linkedin.com/in/johndeveloper.
        
        I'm available for an interview at your convenience.
        
        Best regards,
        John
        '''
    }
    
    # Process inquiry
    result = processor.process_inquiry(inquiry_data)
    print(f"Processed inquiry: {result}")
    
    # Get summary
    summary = processor.get_inquiry_summary(7)
    print(f"Inquiry summary: {summary}")

if __name__ == "__main__":
    main() 