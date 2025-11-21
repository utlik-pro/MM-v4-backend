# Check Messages Command

## Command: `/check-messages`

## Description
Checks and processes new messages from job applicants and HR inquiries.

## Usage
```
/check-messages [options]
```

## Parameters
- `--source`: Message source (email, linkedin, chat) (optional, default: all)
- `--priority`: Priority level (high, medium, low) (optional, default: all)
- `--limit`: Number of messages to process (optional, default: 10)
- `--auto-reply`: Enable automatic responses (optional, default: false)
- `--escalate`: Escalate urgent messages (optional, default: true)

## Examples
```
/check-messages
/check-messages --source email --priority high --limit 5
/check-messages --auto-reply --escalate false
```

## Workflow
1. Connect to message sources
2. Fetch new messages
3. Analyze content and priority
4. Generate appropriate responses
5. Route urgent messages for escalation
6. Update conversation history
7. Schedule follow-ups if needed

## Output
- Summary of processed messages
- Response confirmations
- Escalation notifications
- Follow-up reminders
- Conversation summaries

## Message Processing
- Automatic categorization
- Priority assessment
- Response generation
- Routing decisions
- History tracking

## Integration
- Message Processor Agent
- Email systems
- Chat platforms
- CRM integration
- Calendar scheduling 