# Post Vacancy Command

## Command: `/post-vacancy`

## Description
Posts a new job vacancy to LinkedIn with intelligent content generation and optimization.

## Usage
```
/post-vacancy [options]
```

## Parameters
- `--title`: Job title (required)
- `--company`: Company name (required)
- `--location`: Job location (required)
- `--requirements`: Job requirements (required)
- `--salary`: Salary range (optional)
- `--schedule`: Posting schedule (optional, default: immediate)
- `--template`: Use specific template (optional)

## Examples
```
/post-vacancy --title "Senior Software Engineer" --company "TechCorp" --location "San Francisco, CA" --requirements "Python, React, 5+ years experience"
/post-vacancy --title "Marketing Manager" --company "StartupXYZ" --location "Remote" --salary "$80k-120k" --schedule "tomorrow 9am"
```

## Workflow
1. Validate input parameters
2. Generate optimized job description
3. Create LinkedIn-specific content
4. Schedule post for optimal timing
5. Confirm posting and provide tracking link

## Output
- Posting confirmation with LinkedIn URL
- Scheduled posting time
- Performance tracking information
- Content preview

## Integration
- LinkedIn Poster Agent
- Content optimization tools
- Scheduling system
- Analytics tracking 