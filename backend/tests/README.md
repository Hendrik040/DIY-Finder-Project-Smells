# Backend Test Suite

This directory contains comprehensive unit tests for the DIY Finder backend application.

## Setup

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Ensure the backend dependencies are installed:
```bash
pip install -r requirements.txt
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_utils.py
```

### Run specific test class
```bash
pytest tests/test_utils.py::TestValidateSqlQuery
```

### Run specific test method
```bash
pytest tests/test_utils.py::TestValidateSqlQuery::test_valid_select_query_with_user_id_filter
```

### Run with coverage report
```bash
pytest --cov=. --cov-report=html
```

### Run with verbose output
```bash
pytest -v
```

### Run in parallel (faster)
```bash
pytest -n auto
```

## Test Structure

### test_utils.py
Tests for `backend/utils.py`:
- `TestValidateSqlQuery`: Tests SQL query validation (30+ tests)
  - Valid SELECT queries with proper filters
  - Rejection of dangerous SQL keywords (DROP, DELETE, UPDATE, INSERT, etc.)
  - SQL injection prevention
  - Access control (user_id filtering)
  - Protection of sensitive tables (users table)
  
- `TestSanitizeUsername`: Tests username sanitization (15+ tests)
  - Valid username formats
  - Removal of SQL injection characters
  - Removal of special characters
  - Path traversal prevention
  
- `TestChatWithDatabase`: Tests chat functionality (10+ tests)
  - Valid query execution with parameterized queries
  - Invalid username rejection
  - SQL injection attempt blocking
  - Error handling
  - Message sanitization

- `TestGenerateEmbedding`: Tests embedding generation
- `TestProcessItemData`: Tests item data processing
- `TestExtractDiyMetadata`: Tests metadata extraction

### test_qdrant.py
Tests for `backend/databases/qdrant.py`:
- `TestInitQdrant`: Qdrant initialization tests
- `TestStoreItemVector`: Vector storage tests
- `TestSearchSimilarItems`: Similarity search tests

### test_sql.py
Tests for `backend/databases/sql.py`:
- `TestInitDb`: Database initialization tests
- `TestCreateItem`: Item creation tests
- `TestSearchItems`: Item search tests
- `TestGetUserItems`: User items retrieval tests
- `TestDeletedFunctionality`: Verification that delete_item was removed
- `TestDatabaseSecurity`: SQL injection prevention tests

### test_app.py
Tests for `backend/app.py`:
- `TestHealthEndpoint`: Health check endpoint tests
- `TestAuthEndpoints`: Authentication endpoint tests
- `TestItemEndpoints`: Item management endpoint tests
- `TestChatEndpoint`: Chat endpoint tests
- `TestDeletedEndpoint`: Verification that DELETE endpoint was removed
- `TestCORSConfiguration`: CORS setup tests
- `TestEndpointValidation`: Input validation tests
- `TestErrorHandling`: Error handling tests

## Test Coverage

The test suite aims for high coverage of:
- Security vulnerabilities fixed (SQL injection, validation)
- Removed functionality (delete operations)
- Edge cases and error conditions
- Happy path scenarios
- Input validation
- Error handling

## Key Security Tests

The test suite extensively covers the security improvements made:

1. **SQL Injection Prevention**
   - Parameterized query usage
   - Dangerous keyword blocking
   - Comment injection blocking
   - UNION injection blocking

2. **Input Sanitization**
   - Username sanitization
   - Message text sanitization
   - Length limitations

3. **Access Control**
   - User-specific data filtering
   - Sensitive table protection
   - Query validation

4. **Removed Functionality**
   - Verification that delete endpoints are removed
   - Verification that delete functions don't exist

## Running Tests in CI/CD

Add to your CI pipeline:
```yaml
- name: Run Backend Tests
  run: |
    cd backend
    pip install -r requirements-test.txt
    pytest --cov=. --cov-report=xml
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all existing tests pass
3. Add tests for edge cases
4. Aim for >80% code coverage
5. Document test purpose clearly