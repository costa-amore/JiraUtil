# Refactoring for Testability

## When Tests Fail for Technical Reasons

If test fails due to imports, syntax, or dependency issues, suggest these refactoring patterns:

## 1. Extract Pure Functions

```python

# BAD: Mixed I/O and business logic
def process_assertions(jira_manager, label):
    issues = jira_manager.get_issues_by_label(label)
    for issue in issues:
        print(f"Processing {issue['key']}")

# GOOD: Pure business logic
def process_assertions(issues):
    results = []
    for issue in issues:
        results.append(process_single_issue(issue))
    return results

def print_results(results):
    for result in results:
        print(f"Processing {result['key']}")
```

## 2. Dependency Injection

```python

# BAD: Hard-coded dependency
def run_assert_expectations(jira_instance, label):
    issues = jira_instance.get_issues_by_label(label)

# GOOD: Injected dependency
def run_assert_expectations(issue_fetcher, label):
    issues = issue_fetcher.get_issues_by_label(label)
```

## 3. Interface Segregation

```python

# Create interface
class IssueFetcher(ABC):
    @abstractmethod
    def get_issues_by_label(self, label: str) -> List[dict]:
        pass

# Implement interface
class JiraIssueFetcher(IssueFetcher):
    def get_issues_by_label(self, label: str) -> List[dict]:
        # Real implementation
        pass

# Mock for testing
class MockIssueFetcher(IssueFetcher):
    def get_issues_by_label(self, label: str) -> List[dict]:
        return self.mock_issues
```

## 4. Return Data Instead of Side Effects

```python

# BAD: Direct printing
def process_issues(issues):
    for issue in issues:
        print(f"Result: {issue['key']}")

# GOOD: Return data
def process_issues(issues):
    results = []
    for issue in issues:
        results.append(f"Result: {issue['key']}")
    return results
```
