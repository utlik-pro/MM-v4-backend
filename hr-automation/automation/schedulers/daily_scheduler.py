#!/usr/bin/env python3
"""
Daily Scheduler for HR Automation
Handles scheduled tasks and automated workflows.
"""

import json
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyScheduler:
    def __init__(self, db_path: str = "../database/reports.db"):
        self.db_path = db_path
        self.setup_database()
        self.setup_schedule()
    
    def setup_database(self):
        """Initialize database for scheduled tasks and reports."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create scheduled tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                task_type TEXT NOT NULL,
                schedule_time TEXT NOT NULL,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                status TEXT DEFAULT 'active',
                config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create daily reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date DATE NOT NULL,
                report_type TEXT NOT NULL,
                content TEXT,
                recipients TEXT,
                sent_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create task execution logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                message TEXT,
                duration_seconds REAL,
                FOREIGN KEY (task_id) REFERENCES scheduled_tasks (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_schedule(self):
        """Setup default scheduled tasks."""
        default_tasks = [
            {
                'task_name': 'daily_report',
                'task_type': 'report',
                'schedule_time': '09:00',
                'config': json.dumps({
                    'recipients': ['hr@company.com'],
                    'include_charts': True,
                    'format': 'html'
                })
            },
            {
                'task_name': 'check_messages',
                'task_type': 'automation',
                'schedule_time': '08:00',
                'config': json.dumps({
                    'sources': ['email', 'linkedin'],
                    'auto_reply': True,
                    'escalate': True
                })
            },
            {
                'task_name': 'vacancy_performance_tracking',
                'task_type': 'analytics',
                'schedule_time': '17:00',
                'config': json.dumps({
                    'track_metrics': True,
                    'update_database': True
                })
            },
            {
                'task_name': 'weekly_summary',
                'task_type': 'report',
                'schedule_time': '16:00',
                'config': json.dumps({
                    'day_of_week': 'friday',
                    'recipients': ['hr@company.com', 'management@company.com'],
                    'format': 'pdf'
                })
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for task in default_tasks:
            cursor.execute('''
                INSERT OR IGNORE INTO scheduled_tasks (task_name, task_type, schedule_time, config)
                VALUES (?, ?, ?, ?)
            ''', (task['task_name'], task['task_type'], task['schedule_time'], task['config']))
        
        conn.commit()
        conn.close()
    
    def schedule_daily_report(self):
        """Schedule daily report generation."""
        schedule.every().day.at("09:00").do(self.generate_daily_report)
        logger.info("Scheduled daily report for 09:00")
    
    def schedule_message_check(self):
        """Schedule message checking."""
        schedule.every().day.at("08:00").do(self.check_messages)
        schedule.every().day.at("12:00").do(self.check_messages)
        schedule.every().day.at("16:00").do(self.check_messages)
        logger.info("Scheduled message checks for 08:00, 12:00, and 16:00")
    
    def schedule_vacancy_tracking(self):
        """Schedule vacancy performance tracking."""
        schedule.every().day.at("17:00").do(self.track_vacancy_performance)
        logger.info("Scheduled vacancy tracking for 17:00")
    
    def schedule_weekly_summary(self):
        """Schedule weekly summary report."""
        schedule.every().friday.at("16:00").do(self.generate_weekly_summary)
        logger.info("Scheduled weekly summary for Friday 16:00")
    
    def generate_daily_report(self):
        """Generate and send daily HR report."""
        try:
            logger.info("Generating daily report...")
            
            # Collect daily metrics
            metrics = self.collect_daily_metrics()
            
            # Generate report content
            report_content = self.format_daily_report(metrics)
            
            # Store report
            report_id = self.store_report('daily', report_content)
            
            # Send report
            self.send_report(report_id, report_content)
            
            # Log success
            self.log_task_execution('daily_report', 'success', 'Daily report generated and sent')
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            self.log_task_execution('daily_report', 'error', str(e))
    
    def check_messages(self):
        """Check and process new messages."""
        try:
            logger.info("Checking messages...")
            
            # This would integrate with actual message sources
            # For now, simulating message checking
            
            # Process messages
            processed_count = self.process_messages()
            
            # Log success
            self.log_task_execution('check_messages', 'success', f'Processed {processed_count} messages')
            
        except Exception as e:
            logger.error(f"Error checking messages: {e}")
            self.log_task_execution('check_messages', 'error', str(e))
    
    def track_vacancy_performance(self):
        """Track performance of posted vacancies."""
        try:
            logger.info("Tracking vacancy performance...")
            
            # Get active vacancies
            active_vacancies = self.get_active_vacancies()
            
            # Update performance metrics
            updated_count = 0
            for vacancy in active_vacancies:
                metrics = self.update_vacancy_metrics(vacancy['id'])
                if metrics:
                    updated_count += 1
            
            # Log success
            self.log_task_execution('vacancy_performance_tracking', 'success', f'Updated {updated_count} vacancies')
            
        except Exception as e:
            logger.error(f"Error tracking vacancy performance: {e}")
            self.log_task_execution('vacancy_performance_tracking', 'error', str(e))
    
    def generate_weekly_summary(self):
        """Generate and send weekly summary report."""
        try:
            logger.info("Generating weekly summary...")
            
            # Collect weekly metrics
            metrics = self.collect_weekly_metrics()
            
            # Generate report content
            report_content = self.format_weekly_report(metrics)
            
            # Store report
            report_id = self.store_report('weekly', report_content)
            
            # Send report
            self.send_report(report_id, report_content)
            
            # Log success
            self.log_task_execution('weekly_summary', 'success', 'Weekly summary generated and sent')
            
        except Exception as e:
            logger.error(f"Error generating weekly summary: {e}")
            self.log_task_execution('weekly_summary', 'error', str(e))
    
    def collect_daily_metrics(self) -> Dict:
        """Collect daily HR metrics."""
        # This would integrate with actual data sources
        # For now, returning sample metrics
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'new_applications': 15,
            'interviews_scheduled': 8,
            'interviews_completed': 5,
            'offers_made': 2,
            'offers_accepted': 1,
            'messages_processed': 25,
            'linkedin_posts': 3,
            'linkedin_views': 450,
            'linkedin_applications': 18
        }
    
    def collect_weekly_metrics(self) -> Dict:
        """Collect weekly HR metrics."""
        # This would aggregate daily metrics for the week
        
        return {
            'week_start': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'week_end': datetime.now().strftime('%Y-%m-%d'),
            'total_applications': 85,
            'total_interviews': 35,
            'total_offers': 8,
            'total_hires': 5,
            'avg_time_to_hire': 12.5,
            'cost_per_hire': 2500,
            'source_effectiveness': {
                'linkedin': 45,
                'indeed': 25,
                'referrals': 20,
                'other': 10
            }
        }
    
    def format_daily_report(self, metrics: Dict) -> str:
        """Format daily report content."""
        report = f"""
# Daily HR Report - {metrics['date']}

## Key Metrics
- **New Applications:** {metrics['new_applications']}
- **Interviews Scheduled:** {metrics['interviews_scheduled']}
- **Interviews Completed:** {metrics['interviews_completed']}
- **Offers Made:** {metrics['offers_made']}
- **Offers Accepted:** {metrics['offers_accepted']}

## Communication
- **Messages Processed:** {metrics['messages_processed']}
- **LinkedIn Posts:** {metrics['linkedin_posts']}
- **LinkedIn Views:** {metrics['linkedin_views']}
- **LinkedIn Applications:** {metrics['linkedin_applications']}

## Action Items
- Review applications from today
- Schedule follow-up interviews
- Process pending offers
- Update candidate pipeline

---
*Generated automatically by HR Automation System*
        """
        return report.strip()
    
    def format_weekly_report(self, metrics: Dict) -> str:
        """Format weekly report content."""
        report = f"""
# Weekly HR Summary Report
**Period:** {metrics['week_start']} to {metrics['week_end']}

## Recruitment Summary
- **Total Applications:** {metrics['total_applications']}
- **Total Interviews:** {metrics['total_interviews']}
- **Total Offers:** {metrics['total_offers']}
- **Total Hires:** {metrics['total_hires']}

## Performance Metrics
- **Average Time to Hire:** {metrics['avg_time_to_hire']} days
- **Cost per Hire:** ${metrics['cost_per_hire']}

## Source Effectiveness
- LinkedIn: {metrics['source_effectiveness']['linkedin']}%
- Indeed: {metrics['source_effectiveness']['indeed']}%
- Referrals: {metrics['source_effectiveness']['referrals']}%
- Other: {metrics['source_effectiveness']['other']}%

## Recommendations
- Focus on LinkedIn for high-quality candidates
- Improve referral program engagement
- Optimize interview scheduling process

---
*Generated automatically by HR Automation System*
        """
        return report.strip()
    
    def store_report(self, report_type: str, content: str) -> int:
        """Store report in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO daily_reports (report_date, report_type, content, status)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().date(), report_type, content, 'pending'))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return report_id
    
    def send_report(self, report_id: int, content: str):
        """Send report to recipients."""
        # This would integrate with actual email system
        # For now, just logging the action
        
        logger.info(f"Sending report {report_id} to recipients")
        
        # Update report status
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE daily_reports 
            SET status = 'sent', sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (report_id,))
        
        conn.commit()
        conn.close()
    
    def process_messages(self) -> int:
        """Process new messages (simulated)."""
        # This would integrate with actual message sources
        # For now, returning simulated count
        
        return 5  # Simulated processed message count
    
    def get_active_vacancies(self) -> List[Dict]:
        """Get list of active vacancies."""
        # This would query the actual vacancies database
        # For now, returning sample data
        
        return [
            {'id': 1, 'title': 'Senior Python Developer', 'status': 'active'},
            {'id': 2, 'title': 'Frontend Developer', 'status': 'active'},
            {'id': 3, 'title': 'DevOps Engineer', 'status': 'active'}
        ]
    
    def update_vacancy_metrics(self, vacancy_id: int) -> Optional[Dict]:
        """Update metrics for a specific vacancy."""
        # This would integrate with LinkedIn API or other sources
        # For now, returning sample metrics
        
        return {
            'views': 150,
            'applications': 12,
            'shares': 8,
            'engagement_rate': 0.08
        }
    
    def log_task_execution(self, task_name: str, status: str, message: str):
        """Log task execution details."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get task ID
        cursor.execute('SELECT id FROM scheduled_tasks WHERE task_name = ?', (task_name,))
        task = cursor.fetchone()
        
        if task:
            cursor.execute('''
                INSERT INTO task_logs (task_id, status, message)
                VALUES (?, ?, ?)
            ''', (task[0], status, message))
            
            # Update last run time
            cursor.execute('''
                UPDATE scheduled_tasks 
                SET last_run = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (task[0],))
        
        conn.commit()
        conn.close()
    
    def run_scheduler(self):
        """Run the scheduler continuously."""
        logger.info("Starting HR automation scheduler...")
        
        # Setup all scheduled tasks
        self.schedule_daily_report()
        self.schedule_message_check()
        self.schedule_vacancy_tracking()
        self.schedule_weekly_summary()
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main scheduler execution."""
    scheduler = DailyScheduler()
    
    # Run scheduler
    try:
        scheduler.run_scheduler()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")

if __name__ == "__main__":
    main() 