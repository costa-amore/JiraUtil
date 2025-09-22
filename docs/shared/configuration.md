# Configuration Reference

## Configuration File

The tool looks for credentials in this order:

1. Command line options (`--jira-url`, `--username`, `--password`)
2. `jira_config.env` file in the same directory as the executable
3. Environment variables (`JIRA_URL`, `JIRA_USERNAME`, `JIRA_PASSWORD`)
4. Interactive prompts

## Configuration File Format

Create or edit `jira_config.env` with your Jira credentials:

```env
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_PASSWORD=your_api_token_here
```

## Security Notes

- Use Jira API tokens instead of passwords for better security
- Generate API tokens at: <https://id.atlassian.com/manage-profile/security/api-tokens>
- Keep your credentials secure and never commit them to version control

## Template Value Detection

The tool automatically detects template/placeholder values and will prompt you for real credentials if it finds:

- `yourcompany` in URLs
- `your.email` in usernames
- `your_api` or `token_here` in passwords

## Troubleshooting Configuration

If you see "Template values detected" or connection errors:

1. Edit `jira_config.env` with your real credentials
2. Verify the Jira URL format (use HTTPS)
3. Check your API token is valid and has appropriate permissions
4. Test with command-line options: `--jira-url`, `--username`, `--password`
