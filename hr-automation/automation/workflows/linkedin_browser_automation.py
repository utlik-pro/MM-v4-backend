#!/usr/bin/env python3
"""
LinkedIn Browser Automation
Handles LinkedIn job posting through browser automation instead of API.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path

# Browser automation imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInBrowserAutomation:
    def __init__(self, headless: bool = False, db_path: str = "../database/contacts.db"):
        self.db_path = db_path
        self.headless = headless
        self.driver = None
        self.wait = None
        self.setup_database()
    
    def setup_database(self):
        """Initialize database for LinkedIn automation tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create LinkedIn posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS linkedin_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vacancy_id INTEGER,
                post_content TEXT,
                linkedin_url TEXT,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                views INTEGER DEFAULT 0,
                applications INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                FOREIGN KEY (vacancy_id) REFERENCES vacancies (id)
            )
        ''')
        
        # Create LinkedIn credentials table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS linkedin_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                last_login TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_driver(self):
        """Setup Chrome driver with LinkedIn-specific configurations."""
        try:
            # Use undetected-chromedriver to avoid detection
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # LinkedIn-specific settings
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User agent to look more human
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Initialize driver
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Setup wait
            self.wait = WebDriverWait(self.driver, 20)
            
            logger.info("Chrome driver setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up Chrome driver: {e}")
            raise
    
    def login_to_linkedin(self, email: str, password: str) -> bool:
        """Login to LinkedIn account."""
        try:
            logger.info("Attempting to login to LinkedIn...")
            
            # Navigate to LinkedIn login page
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            email_field.send_keys(email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                logger.info("Successfully logged in to LinkedIn")
                
                # Update credentials in database
                self.update_login_timestamp(email)
                return True
            else:
                logger.error("Login failed - check credentials")
                return False
                
        except Exception as e:
            logger.error(f"Error during LinkedIn login: {e}")
            return False
    
    def navigate_to_job_posting(self):
        """Navigate to LinkedIn job posting page."""
        try:
            logger.info("Navigating to job posting page...")
            
            # Navigate to LinkedIn job posting
            self.driver.get("https://www.linkedin.com/talent/post-a-job")
            time.sleep(3)
            
            # Wait for page to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='job-posting-form']"))
            )
            
            logger.info("Successfully navigated to job posting page")
            
        except Exception as e:
            logger.error(f"Error navigating to job posting page: {e}")
            raise
    
    def fill_job_details(self, job_data: Dict) -> bool:
        """Fill in job posting details."""
        try:
            logger.info("Filling job details...")
            
            # Job title
            title_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='job-title-input']"))
            )
            title_field.clear()
            title_field.send_keys(job_data['title'])
            
            # Company name (usually pre-filled)
            company_field = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='company-name-input']")
            if not company_field.get_attribute('value'):
                company_field.clear()
                company_field.send_keys(job_data['company'])
            
            # Job location
            location_field = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='job-location-input']")
            location_field.clear()
            location_field.send_keys(job_data['location'])
            
            # Job description
            description_field = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='job-description-input']")
            description_field.clear()
            description_field.send_keys(job_data['description'])
            
            # Employment type (if specified)
            if job_data.get('employment_type'):
                employment_dropdown = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='employment-type-dropdown']")
                employment_dropdown.click()
                employment_option = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{job_data['employment_type']}')]")
                employment_option.click()
            
            # Experience level (if specified)
            if job_data.get('experience_level'):
                experience_dropdown = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='experience-level-dropdown']")
                experience_dropdown.click()
                experience_option = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{job_data['experience_level']}')]")
                experience_option.click()
            
            logger.info("Job details filled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error filling job details: {e}")
            return False
    
    def post_job(self) -> Optional[str]:
        """Submit the job posting."""
        try:
            logger.info("Submitting job posting...")
            
            # Click preview button first
            preview_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='preview-button']")
            preview_button.click()
            time.sleep(3)
            
            # Click post button
            post_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='post-button']")
            post_button.click()
            
            # Wait for posting to complete
            time.sleep(5)
            
            # Get the job URL
            job_url = self.driver.current_url
            if "jobs" in job_url:
                logger.info(f"Job posted successfully: {job_url}")
                return job_url
            else:
                logger.error("Job posting failed - could not get job URL")
                return None
                
        except Exception as e:
            logger.error(f"Error posting job: {e}")
            return None
    
    def post_job_vacancy(self, vacancy_data: Dict, email: str, password: str) -> Dict:
        """Complete workflow to post a job vacancy."""
        try:
            # Setup driver
            self.setup_driver()
            
            # Login to LinkedIn
            if not self.login_to_linkedin(email, password):
                raise Exception("LinkedIn login failed")
            
            # Navigate to job posting
            self.navigate_to_job_posting()
            
            # Generate job description
            job_description = self.generate_job_description(vacancy_data)
            
            # Prepare job data
            job_data = {
                'title': vacancy_data['title'],
                'company': vacancy_data['company'],
                'location': vacancy_data['location'],
                'description': job_description,
                'employment_type': vacancy_data.get('employment_type', 'Full-time'),
                'experience_level': vacancy_data.get('experience_level', 'Mid-Senior level')
            }
            
            # Fill job details
            if not self.fill_job_details(job_data):
                raise Exception("Failed to fill job details")
            
            # Post job
            job_url = self.post_job()
            if not job_url:
                raise Exception("Failed to post job")
            
            # Store posting record
            post_id = self.store_posting_record(vacancy_data.get('id'), job_description, job_url)
            
            return {
                'success': True,
                'post_id': post_id,
                'job_url': job_url,
                'posted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in job posting workflow: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            if self.driver:
                self.driver.quit()
    
    def generate_job_description(self, vacancy_data: Dict) -> str:
        """Generate optimized job description."""
        description = f"""
{self.generate_company_intro(vacancy_data['company'])}

## About the Role
We are seeking a talented {vacancy_data['title']} to join our team at {vacancy_data['company']}.

## Key Responsibilities
• Develop and maintain high-quality software solutions
• Collaborate with cross-functional teams
• Participate in code reviews and technical discussions
• Contribute to architectural decisions

## Requirements
{vacancy_data.get('requirements', '• Strong programming skills\n• Experience with modern development practices\n• Excellent problem-solving abilities')}

## Preferred Qualifications
• {vacancy_data.get('preferred_qualifications', 'Experience with agile methodologies\n• Knowledge of cloud platforms\n• Strong communication skills')}

## Benefits
• Competitive salary and benefits package
• Professional development opportunities
• Flexible work arrangements
• Health insurance and wellness programs
• Collaborative and inclusive work environment

## Location
{vacancy_data['location']}

## Employment Type
{vacancy_data.get('employment_type', 'Full-time')}

---
*Join our team and help us build amazing products!*

#hiring #jobs #tech #software #development
        """
        return description.strip()
    
    def generate_company_intro(self, company_name: str) -> str:
        """Generate company introduction."""
        intros = [
            f"{company_name} is a dynamic and innovative company at the forefront of technology.",
            f"At {company_name}, we're passionate about creating solutions that make a difference.",
            f"{company_name} is growing rapidly and we're looking for talented individuals to join our mission.",
            f"Join {company_name} and be part of a team that's shaping the future of technology."
        ]
        import random
        return random.choice(intros)
    
    def store_posting_record(self, vacancy_id: Optional[int], content: str, url: str) -> int:
        """Store LinkedIn posting record in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO linkedin_posts (vacancy_id, post_content, linkedin_url, status)
            VALUES (?, ?, ?, ?)
        ''', (vacancy_id, content, url, 'posted'))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return post_id
    
    def update_login_timestamp(self, email: str):
        """Update last login timestamp for LinkedIn credentials."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE linkedin_credentials 
            SET last_login = CURRENT_TIMESTAMP
            WHERE email = ?
        ''', (email,))
        
        conn.commit()
        conn.close()
    
    def get_posting_analytics(self, post_id: int) -> Dict:
        """Get analytics for a specific posting (simulated)."""
        # This would require additional browser automation to scrape LinkedIn analytics
        # For now, returning simulated data
        
        return {
            'views': 150,
            'applications': 12,
            'shares': 8,
            'engagement_rate': 0.08,
            'last_updated': datetime.now().isoformat()
        }

def main():
    """Example usage of LinkedIn browser automation."""
    automation = LinkedInBrowserAutomation(headless=False)
    
    # Example job data
    vacancy_data = {
        'id': 1,
        'title': 'Senior Python Developer',
        'company': 'TechCorp',
        'location': 'San Francisco, CA',
        'requirements': '• 5+ years of Python development experience\n• Experience with Django, React\n• Knowledge of AWS and cloud platforms',
        'employment_type': 'Full-time',
        'experience_level': 'Senior'
    }
    
    # LinkedIn credentials (should be stored securely)
    email = "your-email@example.com"
    password = "your-password"
    
    # Post job
    result = automation.post_job_vacancy(vacancy_data, email, password)
    print(f"Job posting result: {result}")

if __name__ == "__main__":
    main() 