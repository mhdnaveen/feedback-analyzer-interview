# Feedback Analyzer — Real-world backend processing challenge

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

Add this **Hint** block to your README:

---

### 💡 Hint

Don’t worry about the LLM itself — treat it like a plain HTTP POST that accepts feedback and returns JSON. Focus on the plumbing:

* **Batching**

  * Read the CSV as a stream.
  * Build batches of a tunable size (e.g., **50–200** items).
  * Serialize each batch to a single request body.
  * Keep a small worker pool (e.g., **5–10** concurrent requests).

* **PII Redaction (pre-batch)**

  * Apply regex filters before batching (emails, phone numbers, IPs).
  * Keep redaction deterministic so retries are safe.

* **Rate Limits & Retries**

  * On **HTTP 429** (and transient **5xx**), retry with **backoff + jitter**.
  * If the response includes **`Retry-After`**, sleep for that duration (ignore your computed delay).
  * Cap retries (e.g., **max 5 attempts**) and use a **max backoff** (e.g., **60s**).

That’s it — treat the “LLM” as a black-box API. The challenge is **how you batch and how you back off**.

