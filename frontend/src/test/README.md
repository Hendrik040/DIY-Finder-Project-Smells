# Frontend Test Suite

This directory contains comprehensive unit tests for the DIY Finder frontend application.

## Setup

1. Install test dependencies:
```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event @vitest/ui jsdom
```

2. Ensure vitest configuration is in place (vitest.config.ts in project root)

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests in UI mode
```bash
npm run test:ui
```

### Run tests with coverage
```bash
npm run test:coverage
```

### Run specific test file
```bash
npm test api.test.ts
```

### Run in watch mode
```bash
npm test -- --watch
```

## Test Structure

### api.test.ts
Tests for `frontend/src/lib/api.ts`:
- `Authentication`: Login and registration tests
- `Item Management`: Create and retrieve items tests
- `Search`: Search functionality tests
- `Chat`: Chat functionality tests
- `Deleted Functionality`: Verification deleteItem was removed
- `Error Handling`: Network and API error tests
- `Request Configuration`: HTTP method and header tests

### DashboardView.test.tsx
Tests for `frontend/src/components/views/DashboardView.tsx`:
- `Component Rendering`: Display and layout tests
- `User Interactions`: Button clicks and navigation
- `Deleted Delete Functionality`: Verification delete button is non-functional
- `Item Display Features`: Badge and description rendering
- `View Navigation`: Route navigation tests
- `Error Handling`: Null/undefined data handling
- `Accessibility`: ARIA labels and roles

## Test Coverage

The test suite covers:
- API service methods
- Component rendering
- User interactions
- Error handling
- Removed functionality (delete operations)
- Accessibility features
- Edge cases

## Key Security Tests

1. **Removed Functionality**
   - deleteItem method not in API service
   - Delete button not functional in UI
   - No confirmation dialogs for delete

2. **Error Handling**
   - Network errors
   - Malformed responses
   - Null/undefined data

## Running Tests in CI/CD

Add to your CI pipeline:
```yaml
- name: Run Frontend Tests
  run: |
    cd frontend
    npm install
    npm test -- --coverage
```

## Mocking

The test suite uses Vitest's mocking capabilities:
- `vi.fn()` for function mocks
- `vi.mock()` for module mocks
- `@testing-library/react` for component testing

## Best Practices

1. Test user behavior, not implementation details
2. Use accessible queries (getByRole, getByLabelText)
3. Test error states and edge cases
4. Mock external dependencies
5. Keep tests isolated and independent
6. Use descriptive test names