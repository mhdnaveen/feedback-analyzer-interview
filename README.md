# Feedback Analyzer — Coding Challenge

### Problem Statement

You are building a function that analyzes customer feedback using an LLM API.

Feedback is stored in a CSV file with ~100,000 rows. Each row includes a `free_text` column containing raw customer comments.

### Requirements

Before sending the data to the LLM:

* Redact any PII (emails, phone numbers, IP addresses)
* Batch sanitized feedback into requests
* Handle HTTP 429 rate-limit errors using:

  * choose a backoff method
  * Optional vendor `Retry-After` delay

Use your preferred language, IDE, and coding style to implement the solution.

### Goal

A working service that safely processes feedback and reliably interacts with the LLM at scale.
