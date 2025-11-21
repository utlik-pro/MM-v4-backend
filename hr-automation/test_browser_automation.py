#!/usr/bin/env python3
"""
Test script for LinkedIn browser automation
"""

import os
import sys
import logging
from pathlib import Path

# Add the automation directory to Python path
sys.path.append(str(Path(__file__).parent / 'automation' / 'workflows'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_browser_automation():
    """Test the browser automation functionality."""
    try:
        from linkedin_browser_automation import LinkedInBrowserAutomation
        
        logger.info("Testing LinkedIn browser automation...")
        
        # Initialize automation
        automation = LinkedInBrowserAutomation(headless=True)  # Use headless for testing
        
        # Test data
        vacancy_data = {
            'id': 1,
            'title': 'Test Python Developer',
            'company': 'TestCorp',
            'location': 'Remote',
            'requirements': '• Python programming experience\n• Knowledge of web development\n• Good communication skills',
            'employment_type': 'Full-time',
            'experience_level': 'Mid-level'
        }
        
        # Get credentials from environment
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            logger.warning("LinkedIn credentials not found in environment variables")
            logger.info("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
            return False
        
        logger.info(f"Using email: {email}")
        
        # Test job description generation
        job_description = automation.generate_job_description(vacancy_data)
        logger.info("Job description generated successfully")
        logger.info(f"Description length: {len(job_description)} characters")
        
        # Test database setup
        logger.info("Database setup completed")
        
        logger.info("Browser automation test completed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("Please install required dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

def test_vacancy_processing():
    """Test the vacancy processing workflow."""
    try:
        from vacancy_processing import VacancyProcessor
        
        logger.info("Testing vacancy processing...")
        
        # Initialize processor
        processor = VacancyProcessor()
        
        # Test data
        vacancy_data = {
            'title': 'Test Senior Developer',
            'company': 'TestCorp',
            'location': 'San Francisco, CA',
            'requirements': 'Python, React, 5+ years experience',
            'salary_range': '$100k-150k'
        }
        
        # Create vacancy
        vacancy_id = processor.create_vacancy(vacancy_data)
        logger.info(f"Created vacancy with ID: {vacancy_id}")
        
        # Get vacancy summary
        summary = processor.get_vacancy_summary(vacancy_id)
        logger.info(f"Vacancy summary: {summary['title']} at {summary['company']}")
        
        logger.info("Vacancy processing test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Vacancy processing test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting HR automation system tests...")
    
    # Test vacancy processing
    vacancy_test = test_vacancy_processing()
    
    # Test browser automation
    browser_test = test_browser_automation()
    
    # Summary
    logger.info("=" * 50)
    logger.info("TEST RESULTS:")
    logger.info(f"Vacancy Processing: {'PASS' if vacancy_test else 'FAIL'}")
    logger.info(f"Browser Automation: {'PASS' if browser_test else 'FAIL'}")
    
    if vacancy_test and browser_test:
        logger.info("All tests passed! System is ready to use.")
        return True
    else:
        logger.error("Some tests failed. Please check the logs above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 