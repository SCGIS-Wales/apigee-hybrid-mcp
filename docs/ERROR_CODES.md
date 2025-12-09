# Error Codes Reference

This document provides a comprehensive reference for all error codes used in the Apigee Hybrid MCP Server.

## Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "status": 400,
    "details": {
      "parameter": "param_name",
      "additional": "context"
    },
    "correlation_id": "uuid-for-tracking"
  }
}
```

## Error Codes

### Validation Errors (422)

| Code | Description | Example |
|------|-------------|---------|
| `VALIDATION_ERROR` | Generic validation failure | Input validation failed |
| `INVALID_PARAMETER` | Parameter value is invalid | Invalid email format |
| `MISSING_PARAMETER` | Required parameter not provided | Missing required field 'organization' |
| `EXPIRED_PARAMETER` | Time-bound parameter has expired | Authentication token expired |

**Example Response:**
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid parameter 'email': must be valid email format",
    "status": 422,
    "details": {
      "parameter": "email",
      "reason": "must be valid email format"
    },
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

### Authentication Errors (401)

| Code | Description | Example |
|------|-------------|---------|
| `AUTHENTICATION_ERROR` | Authentication failed | Invalid or missing credentials |

**Example Response:**
```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Authentication failed",
    "status": 401,
    "details": {
      "reason": "token_expired"
    },
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

### Authorization Errors (403)

| Code | Description | Example |
|------|-------------|---------|
| `AUTHORIZATION_ERROR` | Insufficient permissions | User lacks required permissions |

**Example Response:**
```json
{
  "error": {
    "code": "AUTHORIZATION_ERROR",
    "message": "Access denied",
    "status": 403,
    "details": {
      "resource": "teams/admin"
    },
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

### Resource Errors

| Code | Status | Description | Example |
|------|--------|-------------|---------|
| `RESOURCE_NOT_FOUND` | 404 | Resource doesn't exist | Team not found |
| `RESOURCE_ALREADY_EXISTS` | 409 | Resource already exists | Team with this name already exists |

**Example Response (404):**
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Team not found: team-123",
    "status": 404,
    "details": {
      "resource_type": "team",
      "resource_id": "team-123"
    },
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

### Timeout Errors (408)

| Code | Description | Example |
|------|-------------|---------|
| `TIMEOUT_ERROR` | Operation timed out | Request exceeded timeout limit |

**Example Response:**
```json
{
  "error": {
    "code": "TIMEOUT_ERROR",
    "message": "Operation timed out: API request",
    "status": 408,
    "details": {
      "operation": "API request",
      "timeout_seconds": 30
    },
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

### External Service Errors (502/503)

| Code | Description | Example |
|------|-------------|---------|
| `EXTERNAL_SERVICE_ERROR` | External service failure | Apigee API unavailable |

**Example Response:**
```json
{
  "error": {
    "code": "EXTERNAL_SERVICE_ERROR",
    "message": "apigee_api: Service temporarily unavailable",
    "status": 503,
    "details": {
      "service": "apigee_api"
    },
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

### Generic Application Errors (500)

| Code | Description | Example |
|------|-------------|---------|
| `APP_ERROR` | Generic application error | Unexpected internal error |

**Example Response:**
```json
{
  "error": {
    "code": "APP_ERROR",
    "message": "An unexpected error occurred",
    "status": 500,
    "details": {},
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

## Correlation IDs

Every error includes a unique `correlation_id` (UUID v4) for tracking and troubleshooting. When reporting issues:

1. Include the full correlation ID
2. Provide the timestamp of the error
3. Describe the operation that failed

## Parameter Validation

### Required Parameters

Required parameters are validated before processing. Missing required parameters result in `MISSING_PARAMETER` errors.

### Parameter Constraints

Parameters may have additional constraints:

- **Type**: Must be specific type (string, integer, etc.)
- **Format**: Must match pattern (email, UUID, etc.)
- **Range**: Must be within bounds (1-600 for timeout)
- **Enum**: Must be one of allowed values
- **Length**: Minimum/maximum length for strings

### Time-Bound Parameters

Parameters like tokens and session IDs may have expiration times. Expired parameters result in `EXPIRED_PARAMETER` errors with the expiration timestamp in details.

## Sensitive Data Redaction

Sensitive fields (tokens, passwords, keys, credentials) are automatically redacted in:

- Error details
- Log messages
- Debug output

Fields are redacted as `***REDACTED***` to prevent credential leakage.

## Troubleshooting

### Common Error Scenarios

#### 1. Missing Required Parameter

```
Error Code: MISSING_PARAMETER
Solution: Ensure all required parameters are provided
```

#### 2. Invalid Parameter Format

```
Error Code: INVALID_PARAMETER
Solution: Check parameter format (e.g., email, UUID)
```

#### 3. Resource Not Found

```
Error Code: RESOURCE_NOT_FOUND
Solution: Verify the resource ID exists
```

#### 4. Authentication Failed

```
Error Code: AUTHENTICATION_ERROR
Solution: Check credentials are valid and not expired
```

#### 5. Request Timeout

```
Error Code: TIMEOUT_ERROR
Solution: Retry the request or increase timeout
```

### Getting Help

When seeking help with errors:

1. **Include the correlation ID** from the error response
2. **Describe the operation** you were attempting
3. **Provide the error code and message**
4. **Check logs** for additional context (if available)

## HTTP Status Code Mapping

| Status Code | Error Category | Description |
|-------------|----------------|-------------|
| 400 | Bad Request | Generic client error |
| 401 | Unauthorized | Authentication required/failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 408 | Request Timeout | Operation timed out |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 502 | Bad Gateway | External service error |
| 503 | Service Unavailable | Service temporarily down |
