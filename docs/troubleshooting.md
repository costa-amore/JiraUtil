# Troubleshooting Guide

Common issues and solutions for JiraUtil.

## Connection Issues

### "Failed to connect to Jira"

**Symptoms:**

- Error message: "Failed to connect to Jira"
- Tool exits with error code 1

**Solutions:**

1. **Check Jira URL format:**
   - Use: `https://yourcompany.atlassian.net`
   - Avoid: `http://` (use HTTPS)
   - Avoid: trailing slashes

2. **Verify API token:**

   - Generate new token at: <https://id.atlassian.com/manage-profile/security/api-tokens>
   - Use API token, not password
   - Ensure token has appropriate permissions

3. **Check network connectivity:**
   - Test URL in browser
   - Check firewall/proxy settings
   - Verify VPN connection if required

4. **Verify credentials:**
   - Test with `--jira-url`, `--username`, `--password` options
   - Check `jira_config.env` file format

### "Template values detected"

**Symptoms:**

- Prompted for credentials even with config file
- Message about template values

**Solutions:**

1. **Edit `jira_config.env`:**

   ```env
   JIRA_URL=https://yourcompany.atlassian.net
   JIRA_USERNAME=your.email@company.com
   JIRA_PASSWORD=your_actual_api_token
   ```

2. **Remove template patterns:**
   - Avoid: `yourcompany`, `your.email`, `your_api_token`
   - Use real values instead

## Data Issues

### "No issues found"

**Symptoms:**

- Message: "No issues found" or "0 issues processed"
- Empty results

**Solutions:**

1. **Check label name:**
   - Verify label exists in Jira
   - Check spelling and case sensitivity
   - Try: `JiraUtil rt --help` to see default label

2. **Verify permissions:**
   - Ensure you can view issues with that label
   - Check Jira project permissions
   - Test with a different label

3. **Check JQL query:**
   - Tool uses: `labels = "your-label"`
   - Verify label format in Jira

### "Summary doesn't match expected pattern"

**Symptoms:**

- Issues skipped with pattern mismatch message
- No status updates performed

**Solutions:**

1. **Check summary format:**
   - Required: `I was in <status1> - expected to be in <status2>`
   - Example: `I was in To Do - expected to be in In Progress`

2. **Verify status names:**
   - Use exact Jira status names
   - Check case sensitivity
   - Avoid extra spaces

## File Issues

### "File not found" or "Permission denied"

**Symptoms:**

- Error opening CSV files
- Cannot write output files

**Solutions:**

1. **Check file paths:**
   - Use absolute paths if needed
   - Avoid spaces in file names
   - Check file exists

2. **Verify permissions:**
   - Ensure read access to input files
   - Ensure write access to output directory
   - Run as administrator if needed (Windows)

3. **Check file format:**
   - Ensure file is valid CSV
   - Check file encoding (UTF-8 recommended)

### "Invalid field name"

**Symptoms:**

- Error when extracting field values
- Field not found in CSV

**Solutions:**

1. **Check field names:**
   - Use exact column headers from CSV
   - Check spelling and case
   - Common names: "Assignee", "Status", "Parent key"

2. **Verify CSV format:**
   - Check first row contains headers
   - Ensure consistent column structure
   - Avoid merged cells

## Performance Issues

### "Slow execution" or "Timeout"

**Symptoms:**

- Long wait times
- Connection timeouts

**Solutions:**

1. **Reduce scope:**
   - Use more specific labels
   - Process smaller batches
   - Filter issues in Jira first

2. **Check network:**
   - Test connection speed
   - Use wired connection if possible
   - Check for network issues

3. **Optimize queries:**
   - Use specific project filters
   - Limit date ranges
   - Avoid very broad searches

## Platform-Specific Issues

### Windows Issues

**"Access denied" errors:**

- Run Command Prompt as Administrator
- Check antivirus software
- Verify file permissions

**"Python not found":**

- Executable is self-contained
- No Python installation required
- Check if file is corrupted

### macOS/Linux Issues

**"Permission denied" on executable:**

```bash
chmod +x JiraUtil
```

**"Command not found":**

```bash
./JiraUtil --help
```

## Getting Help

### Debug Information

1. **Enable verbose output:**
   - Use `--help` to see all options
   - Check error messages carefully

2. **Test with simple commands:**

   ```bash
   JiraUtil --help
   JiraUtil CsvExport --help
   ```

3. **Verify configuration:**
   - Check `jira_config.env` file
   - Test with command-line credentials

### Common Solutions

1. **Restart the tool:**
   - Close and reopen
   - Clear any cached data

2. **Update configuration:**
   - Regenerate API token
   - Update Jira URL if changed
   - Verify permissions

3. **Check Jira status:**
   - Verify Jira instance is accessible
   - Check for maintenance windows
   - Test with Jira web interface

### When to Contact Support

Contact your system administrator if:

- Jira instance is down
- Permission issues persist
- Network connectivity problems
- Tool crashes repeatedly

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 0 | Success | - |
| 1 | General error | Check error message |
| 2 | Invalid arguments | Use `--help` for correct syntax |
| 3 | File not found | Check file paths |
| 4 | Permission denied | Check file permissions |
| 5 | Connection failed | Check Jira credentials and network |

---

*For additional help, check the user guide or command reference.*

---

[🏠 Home](../README.md) | [← Command Reference](command-reference.md) | [User Guide →](../user-guide.md)
