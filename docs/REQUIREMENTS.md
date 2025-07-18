# **Requirements Document: Anymouse Anonymization Service (AWS Lambda)**

[See the discussion link](https://chatgpt.com/c/687812c9-c764-800e-b8c9-4c4cf9949ad6)

---

## **Purpose**

Provide a stateless microservice to anonymize and deanonymize sensitive data passing through administrative/accounting integrations (Jane EMR, Shopify, QBO, etc.), or semi-structured communication (emails, notes), via tokenization and lookup. The service must support regulatory compliance and minimize patient identification risk, including in contexts with multiple personal names.

---

## **Functional Requirements**

### 1. **Tokenization / Anonymization**

* **Input:** Raw data payloads (JSON/CSV/email text) containing potentially identifying fields or entities (names, emails, dates, etc.).
* **Process:**

  * Extract target fields/entities (e.g., patient name, email, address, invoice IDs) using a combination of field config, regex, and Named Entity Recognition (NER).
  * For free-form text (such as emails), detect personal names, organizations, and other entities using NER (e.g., via spaCy, AWS Comprehend, or similar).
  * Replace detected entities with unique, deterministic tokens (e.g., `[name1]`, `[name2]`, etc.).
  * **Stateless:** The mapping of tokens to original values is included in the response JSON; the service retains no mapping or state after the response.
  * Non-identifying fields/entities pass through unchanged.
* **Output:** An anonymized manifest (see below), suitable for downstream integration, and designed so the structure could easily be adapted to an array-of-objects pattern for future batch support.

### 2. **Lookup / Deanonymization**

* **Input:** Payloads or messages with tokens in place of real values and a corresponding tokens dictionary.
* **Process:**

  * Identify token placeholders in the message/payload.
  * Use the provided tokens dictionary to replace tokens with original values.
  * **Stateless:** No server-side lookup; mapping is fully client-provided.
* **Output:** Deanonymized (rehydrated) message or payload.

### 3. **Pre/Post-Processing Hooks**

* **Extraction:** Configurable logic to identify and extract fields or entities for anonymization, including support for:

  * Field mappings for structured data (e.g., `patient_name` → tokenize).
  * Regex and NER for semi-structured/free-form data (e.g., “Jane Doe,” “Dr. McCulloch”).
* **Reinjection:** Map tokens back to original values using only client-provided mappings.

### 4. **Stateless Lambda Operation**

* **Stateless:** The Lambda function stores nothing between requests; all mapping data is contained in the response and must be managed by the client.

---

## **Non-Functional Requirements**

* **Security:**

  * Lambda must require an API key, IAM role, or other best-practice authorization to prevent unauthorized use.
  * No mapping or token data is ever stored server-side.
* **Performance:**

  * Must handle \~10–100 requests/sec with sub-second latency.
  * Must scale with AWS Lambda’s automatic scaling.
* **Auditing/Logging:**

  * Only minimal access logs (timestamp, status, possibly origin IP).
  * Audit logs must not contain any payload, PII, tokens, or mappings.
* **Configurable Field List:**

  * Field mappings, regexes, and NER models are externally configurable (JSON, YAML, or fetched from S3/SSM).

---

## **API Design**

### **Endpoints**

* `POST /anonymize`

  * **Input:**

    ```json
    {
      "payload": {
        "name": "Alice",
        "email": "alice@email.com",
        "date": "2023-10-01"
      },
      "config": {
        "fields": ["name", "email", "date"]
      }
    }
    ```

    or, for free-form text:

    ```json
    {
      "payload": "Hello,\n\nI have a question for Dr. McCulloch regarding my prescription. ...\nThank you,\nJane Smith"
    }
    ```
  * **Output:**

    ```json
    {
      "message": "Hello,\n\nI have a question for [name1] regarding my prescription. ...\nThank you,\n[name2]",
      "tokens": {
        "name1": "Dr. McCulloch",
        "name2": "Jane Smith"
      },
      "fields": ["PERSON"]
    }
    ```

    * `message`: String template with token placeholders.
    * `tokens`: Dictionary mapping placeholder names to real values.
    * `fields`: List of fields/entities processed or available for tokenization.

* `POST /deanonymize`

  * **Input:**

    ```json
    {
      "message": "Hello,\n\nI have a question for [name1] regarding my prescription. ...\nThank you,\n[name2]",
      "tokens": {
        "name1": "Dr. McCulloch",
        "name2": "Jane Smith"
      }
    }
    ```
  * **Output:**

    ```json
    {
      "message": "Hello,\n\nI have a question for Dr. McCulloch regarding my prescription. ...\nThank you,\nJane Smith"
    }
    ```

* `POST /config/test`

  * (Validate/test a new extraction/config payload.)

---

### **Email Example Use Case**

**Input email:**

```
Jane Doe<my.email@emailhost.com>
Mon, Jan 01, 12:45 PM
to me

Hello,

I have a question for Dr. McCulloch regarding my pms-progesterone prescription. ...
Thank you,
Jane Smith
Sent from my iPhone
```

**Expected anonymized output:**

```json
{
  "message": "Jane Doe<my.email@emailhost.com>\nMon, Jan 01, 12:45 PM\nto me\n\nHello,\n\nI have a question for [name1] regarding my pms-progesterone prescription. ...\nThank you,\n[name2]\nSent from my iPhone",
  "tokens": {
    "name1": "Dr. McCulloch",
    "name2": "Jane Smith"
  },
  "fields": ["PERSON"]
}
```

* The Lambda must tokenize all detected PERSON entities, supporting emails where multiple distinct names appear (sender, recipient, doctor, patient, etc.).

---

## **Implementation Constraints**

* **Language:** Python (preferred for AWS Lambda, robust NER/NLP library support).
* **Entity Extraction:** Use spaCy (with English NER model) or AWS Comprehend for Named Entity Recognition, falling back to regexes for headers if needed.
* **Storage:** No data stored server-side; all mapping is handled by the client.
* **Deployment:** AWS Lambda + API Gateway; configuration in S3 or SSM.
* **Access:** Auth via AWS IAM, API key, or similar; do not expose endpoint without protection.

---

## **Edge Cases & Open Questions**

* What is the best-practice method for Lambda API authorization? (API key, IAM, Cognito, etc.)
* Bulk/batch: Not supported initially, but all output signatures should be array-friendly for future extension.
* No data retention: All mappings/tokens must be returned to and managed by the client; no server-side persistence.
* “Multi-tenant” concerns removed: Each invocation is stateless and does not need to distinguish between clients internally.

---

**Next Steps:**

* Confirm field/entity extraction spec and sample payloads for each integration.
* Decide on API authorization mechanism for Lambda.
* Finalize config interface (S3/SSM/inline).
* Prototype with spaCy and evaluate Lambda deployment size/performance.

---
