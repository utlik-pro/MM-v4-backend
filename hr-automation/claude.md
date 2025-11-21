# HR Automation System - Claude AI Integration

## Overview

This HR automation system leverages Claude AI to streamline and automate various HR processes including job posting, message processing, contact management, and report generation.

## System Architecture

### Core Components

1. **Claude AI Agents** - Specialized AI agents for different HR functions
2. **Automation Workflows** - Python scripts for processing and automation
3. **Scheduled Tasks** - Automated daily/weekly tasks
4. **Database Storage** - SQLite databases for data persistence
5. **Browser Automation** - LinkedIn web interface automation

### Directory Structure

```
hr-automation/
├── .claude/                    # Claude AI configuration
│   ├── agents/                 # AI agent definitions
│   ├── commands/               # Slash command definitions
│   └── config.json            # Main configuration
├── .mcp.json                  # MCP server configuration
├── automation/                 # Python automation scripts
│   ├── workflows/             # Main workflow scripts
│   └── schedulers/            # Scheduled task management
├── database/                  # SQLite databases
└── claude.md                 # This documentation
```

## Claude AI Agents

### 1. LinkedIn Poster Agent
- **Purpose**: Automates job posting to LinkedIn
- **Capabilities**: Content generation, optimization, scheduling, performance tracking
- **Integration**: LinkedIn API, content optimization tools

### 2. Message Processor Agent
- **Purpose**: Processes incoming messages and inquiries
- **Capabilities**: Content analysis, response generation, routing, conversation tracking
- **Integration**: Email systems, chat platforms, CRM

### 3. Contact Manager Agent
- **Purpose**: Manages contact database and relationships
- **Capabilities**: Contact storage, categorization, communication tracking, data quality
- **Integration**: CRM systems, contact platforms

### 4. Report Generator Agent
- **Purpose**: Generates comprehensive HR reports
- **Capabilities**: Daily/weekly reports, analytics, data visualization, insights
- **Integration**: Database systems, reporting tools

## Commands

### `/post-vacancy`
Posts a new job vacancy to LinkedIn with intelligent content generation.

**Usage:**
```
/post-vacancy --title "Senior Developer" --company "TechCorp" --location "San Francisco" --requirements "Python, React, 5+ years"
```

### `/check-messages`
Checks and processes new messages from various sources.

**Usage:**
```
/check-messages --source email --priority high --auto-reply
```

### `/daily-report`
Generates and sends daily HR reports.

**Usage:**
```
/daily-report --format pdf --recipients "hr@company.com"
```

## Automation Workflows

### Vacancy Processing Workflow
- **File**: `automation/workflows/vacancy_processing.py`
- **Purpose**: Handles complete job posting workflow
- **Features**: Database management, content generation, performance tracking

### Development Inquiry Workflow
- **File**: `automation/workflows/development_inquiry.py`
- **Purpose**: Processes technical candidate inquiries
- **Features**: Contact extraction, inquiry analysis, automated responses

### Daily Scheduler
- **File**: `automation/schedulers/daily_scheduler.py`
- **Purpose**: Manages scheduled tasks and automation
- **Features**: Daily reports, message checking, performance tracking

## Database Schema

### Contacts Database (`contacts.db`)
- **contacts**: Contact information and profiles
- **vacancies**: Job posting records
- **applications**: Job application data
- **development_inquiries**: Technical inquiry records

### Reports Database (`reports.db`)
- **scheduled_tasks**: Task scheduling information
- **daily_reports**: Generated report storage
- **task_logs**: Execution logs and metrics

## Browser Automation Integration

The system uses browser automation for LinkedIn integration:

- **LinkedIn**: Job posting through web interface using Selenium/Playwright
- **Browser Automation**: Undetected ChromeDriver for anti-detection
- **Email**: Message processing and notifications
- **Calendar**: Scheduling and meeting management
- **Database**: Data storage and retrieval

## Setup and Configuration

### 1. Environment Variables
Set up the following environment variables for browser automation:

```bash
# LinkedIn Browser Automation
LINKEDIN_EMAIL=your-linkedin-email@example.com
LINKEDIN_PASSWORD=your-linkedin-password

# Browser Settings
CHROME_HEADLESS=false
CHROME_USER_DATA_DIR=./chrome_user_data

# Email Configuration
EMAIL_SERVER=smtp.gmail.com
EMAIL_USERNAME=your_email
EMAIL_PASSWORD=your_password

# Calendar API
CALENDAR_API_KEY=your_api_key
CALENDAR_CALENDAR_ID=your_calendar_id
```

### 2. Python Dependencies
Install required Python packages:

```bash
pip install -r requirements.txt

# Install Chrome WebDriver
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

### 3. Database Initialization
The system automatically creates necessary database tables on first run.

## Usage Examples

### Posting a Job Vacancy
```python
from automation.workflows.vacancy_processing import VacancyProcessor

processor = VacancyProcessor()
vacancy_data = {
    'title': 'Senior Python Developer',
    'company': 'TechCorp',
    'location': 'San Francisco, CA',
    'requirements': 'Python, Django, React, 5+ years experience',
    'salary_range': '$120k-180k'
}

vacancy_id = processor.create_vacancy(vacancy_data)
result = processor.post_to_linkedin(vacancy_id)
```

### Processing Development Inquiries
```python
from automation.workflows.development_inquiry import DevelopmentInquiryProcessor

processor = DevelopmentInquiryProcessor()
inquiry_data = {
    'name': 'John Developer',
    'email': 'john@example.com',
    'message': 'I have 5+ years experience with Python and React...'
}

result = processor.process_inquiry(inquiry_data)
```

### Running the Scheduler
```python
from automation.schedulers.daily_scheduler import DailyScheduler

scheduler = DailyScheduler()
scheduler.run_scheduler()
```

## Monitoring and Logging

The system includes comprehensive logging and monitoring:

- **Task Execution Logs**: Track all automated task executions
- **Performance Metrics**: Monitor system performance and response times
- **Error Handling**: Comprehensive error logging and recovery
- **Database Logs**: Track all database operations

## Security and Compliance

### Data Protection
- All sensitive data is encrypted in transit and at rest
- GDPR compliance for contact data management
- Access controls and audit trails

### API Security
- Secure API key management
- Rate limiting and request validation
- Error handling without data exposure

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check file permissions for database directories
   - Ensure SQLite is properly installed

2. **MCP Connection Issues**
   - Verify environment variables are set correctly
   - Check network connectivity to external services

3. **Scheduler Not Running**
   - Check system time and timezone settings
   - Verify Python dependencies are installed

### Log Analysis
Check the following log files for debugging:
- Application logs in the automation directory
- Database logs in the database directory
- System logs for scheduler issues

## Future Enhancements

### Planned Features
- Advanced AI content generation
- Multi-platform job posting
- Advanced analytics and reporting
- Integration with additional HR systems
- Mobile application support

### Scalability Improvements
- Database optimization for large datasets
- Distributed processing capabilities
- Cloud deployment options
- API rate limiting and caching

## Support and Maintenance

### Regular Maintenance Tasks
- Database cleanup and optimization
- Log file rotation and cleanup
- Performance monitoring and tuning
- Security updates and patches

### Backup Procedures
- Regular database backups
- Configuration file backups
- Log file archiving
- Disaster recovery procedures

---

*This documentation is maintained by the HR Automation System team. For questions or support, please contact the development team.* 