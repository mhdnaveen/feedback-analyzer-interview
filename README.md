# feedback-analyzer-interview
Coding challenge: process customer feedback by redacting PII, batching requests, and handling LLM rate limits.

**Problem Statement**
You are building a service that analyzes customer feedback using an LLM API.
Feedbacks are stored in a CSV file with around 100,000 rows, each containing a column named free_text.
 
Before sending the text to the LLM, you must:
Redact any PII (personally identifiable information) such as emails, phone numbers and IP addresses.
Batch the sanitized feedbacks and send them to the LLM API.
Handle rate-limit errors (HTTP 429) using exponential backoff with jitter and an optional vendor Retry-After delay.
Use your IDE and preferred code style to implement the solution.
