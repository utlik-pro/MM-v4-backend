# HR Automation System

A comprehensive HR automation system powered by Claude AI that streamlines recruitment, candidate management, and reporting processes.

## 🚀 Features

- **AI-Powered Job Posting**: Automatically generate and post optimized job descriptions to LinkedIn using browser automation
- **Smart Message Processing**: Analyze and respond to candidate inquiries using AI
- **Contact Management**: Intelligent contact database with relationship tracking
- **Automated Reporting**: Generate daily and weekly HR reports with insights
- **Scheduled Automation**: Run tasks automatically at optimal times
- **Multi-Platform Integration**: Connect with LinkedIn, email, calendar, and CRM systems

## 📁 Project Structure

```
hr-automation/
├── .claude/                    # Claude AI configuration
│   ├── agents/                 # AI agent definitions
│   │   ├── linkedin-poster.md
│   │   ├── message-processor.md
│   │   ├── contact-manager.md
│   │   └── report-generator.md
│   ├── commands/               # Slash command definitions
│   │   ├── post-vacancy.md
│   │   ├── check-messages.md
│   │   └── daily-report.md
│   └── config.json            # Main configuration
├── .mcp.json                  # MCP server configuration
├── automation/                 # Python automation scripts
│   ├── workflows/             # Main workflow scripts
│   │   ├── vacancy_processing.py
│   │   └── development_inquiry.py
│   └── schedulers/            # Scheduled task management
│       └── daily_scheduler.py
├── database/                  # SQLite databases
│   ├── contacts.db
│   └── reports.db
├── requirements.txt           # Python dependencies
├── claude.md                 # Detailed documentation
└── README.md                 # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Claude AI access
- Google Chrome browser
- LinkedIn account credentials
- Email server access (optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hr-automation
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your credentials
   LINKEDIN_EMAIL=your-linkedin-email@example.com
   LINKEDIN_PASSWORD=your-linkedin-password
   EMAIL_SERVER=smtp.gmail.com
   EMAIL_USERNAME=your_email
   EMAIL_PASSWORD=your_password
   ```

4. **Setup browser automation**
   ```bash
   # Install Chrome WebDriver
   python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
   
   # Initialize databases
   python automation/workflows/vacancy_processing.py
   ```

## 🎯 Quick Start

### Post a Job Vacancy

```bash
# Using Claude command
/post-vacancy --title "Senior Python Developer" --company "TechCorp" --location "San Francisco" --requirements "Python, React, 5+ years"

# Using Python directly
python automation/workflows/vacancy_processing.py
```

### Check Messages

```bash
# Using Claude command
/check-messages --source email --priority high --auto-reply

# Using Python directly
python automation/workflows/development_inquiry.py
```

### Generate Daily Report

```bash
# Using Claude command
/daily-report --format pdf --recipients "hr@company.com"

# Using Python directly
python automation/schedulers/daily_scheduler.py
```

## 🤖 Claude AI Agents

### LinkedIn Poster Agent
- Generates optimized job descriptions
- Uses browser automation for posting
- Schedules posts at optimal times
- Tracks performance metrics
- A/B tests different formats

### Message Processor Agent
- Analyzes incoming messages
- Generates personalized responses
- Routes urgent inquiries
- Tracks conversation history

### Contact Manager Agent
- Manages candidate database
- Tracks communication history
- Segments contacts by category
- Maintains data quality

### Report Generator Agent
- Creates daily/weekly reports
- Generates insights and trends
- Provides data visualizations
- Distributes to stakeholders

## 📊 Database Schema

### Contacts Database (`database/contacts.db`)
- **contacts**: Contact information and profiles
- **vacancies**: Job posting records
- **applications**: Job application data
- **development_inquiries**: Technical inquiry records

### Reports Database (`database/reports.db`)
- **scheduled_tasks**: Task scheduling information
- **daily_reports**: Generated report storage
- **task_logs**: Execution logs and metrics

## 🔧 Configuration

### Claude Configuration (`.claude/config.json`)
```json
{
  "name": "HR Automation System",
  "version": "1.0.0",
  "agents": {
    "linkedin-poster": {
      "file": "agents/linkedin-poster.md",
      "description": "Handles LinkedIn job posting automation"
    }
  },
  "settings": {
    "database_path": "../database/",
    "automation_path": "../automation/",
    "default_timezone": "UTC"
  }
}
```

### MCP Configuration (`.mcp.json`)
```json
{
  "mcpServers": {
    "linkedin": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-linkedin"]
    }
  }
}
```

## 📈 Usage Examples

### Python API Usage

```python
from automation.workflows.vacancy_processing import VacancyProcessor

# Create vacancy processor
processor = VacancyProcessor()

# Post a job
vacancy_data = {
    'title': 'Senior Python Developer',
    'company': 'TechCorp',
    'location': 'San Francisco, CA',
    'requirements': 'Python, Django, React, 5+ years experience',
    'salary_range': '$120k-180k'
}

vacancy_id = processor.create_vacancy(vacancy_data)
result = processor.post_to_linkedin(vacancy_id)
print(f"Posted vacancy: {result}")
```

### Development Inquiry Processing

```python
from automation.workflows.development_inquiry import DevelopmentInquiryProcessor

# Process inquiry
processor = DevelopmentInquiryProcessor()
inquiry_data = {
    'name': 'John Developer',
    'email': 'john@example.com',
    'message': 'I have 5+ years experience with Python and React...'
}

result = processor.process_inquiry(inquiry_data)
print(f"Processed inquiry: {result}")
```

## 🔄 Scheduled Tasks

The system includes automated scheduling for:

- **Daily Reports**: Generated at 9:00 AM
- **Message Checking**: 8:00 AM, 12:00 PM, 4:00 PM
- **Performance Tracking**: 5:00 PM daily
- **Weekly Summaries**: Friday at 4:00 PM

### Running the Scheduler

```bash
# Start the scheduler
python automation/schedulers/daily_scheduler.py

# Or run as a service
nohup python automation/schedulers/daily_scheduler.py &
```

## 🔒 Security & Compliance

- **Data Encryption**: All sensitive data encrypted in transit and at rest
- **GDPR Compliance**: Contact data management follows GDPR guidelines
- **Access Controls**: Role-based access control system
- **Audit Trails**: Comprehensive logging of all operations

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database permissions
   ls -la database/
   # Ensure SQLite is installed
   python -c "import sqlite3; print('SQLite OK')"
   ```

2. **Browser Automation Issues**
   ```bash
   # Verify environment variables
   echo $LINKEDIN_EMAIL
   echo $EMAIL_SERVER
   
   # Check Chrome installation
   google-chrome --version
   
   # Verify WebDriver installation
   python -c "from webdriver_manager.chrome import ChromeDriverManager; print('WebDriver OK')"
   ```

3. **Scheduler Not Running**
   ```bash
   # Check system time
   date
   # Verify dependencies
   pip list | grep schedule
   ```

### Log Analysis

Check logs in:
- `automation/` - Application logs
- `database/` - Database operation logs
- System logs for scheduler issues

## 📚 Documentation

- **[Claude Integration Guide](claude.md)** - Detailed Claude AI setup and usage
- **[API Reference](docs/api.md)** - Python API documentation
- **[Configuration Guide](docs/config.md)** - System configuration options
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [claude.md](claude.md)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@company.com

## 🔮 Roadmap

### Upcoming Features
- [ ] Multi-platform job posting (Indeed, Glassdoor)
- [ ] Advanced AI content generation
- [ ] Mobile application
- [ ] Advanced analytics dashboard
- [ ] Integration with ATS systems

### Planned Improvements
- [ ] Cloud deployment options
- [ ] Real-time notifications
- [ ] Advanced reporting features
- [ ] Machine learning insights

---

**Made with ❤️ by the HR Automation Team** 