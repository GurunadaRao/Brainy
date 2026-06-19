# Security Review Template

## 1. Authentication & Authorization
- Verify endpoint security controls.
- Role-based access control policies.

## 2. Injection & Input Sanitization
- SQL injection prevention (using SQLAlchemy parameters).
- Cypher query sanitation (using parameterized cypher inputs).
- Prompt injection prevention for extraction tasks.

## 3. Data Protection
- Encryption in transit (TLS) and at rest.
