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
  * Replace detected entities with unique, deterministic tokens (e.g., `[name1]`, `[name2]`, etc.; tokens may be UUIDv4, hash, or salted hash under the hood).
  * Store a mapping (token → real value) in a secure, isolated data store (e.g., DynamoDB, encrypted S3, or RDS).
  * Non-identifying fields/entities pass through unchanged.
* **Output:** An anonymized manifest (see below), suitable for downstream integration.

### 2. **Lookup / Deanonymization**

* **Input:** Payloads or messages with tokens in place of real values and a corresponding tokens dictionary.
* **Process:**

  * Identify token placeholders in the message/payload.
  * Lookup token mappings and replace with the original value.
* **Output:** Deanonymized (rehydrated) message or payload.

### 3. **Pre/Post-Processing Hooks**

* **Extraction:** Configurable logic to identify and extract fields or entities for anonymization, including support for:

  * Field mappings for structured data (e.g., `patient_name` → tokenize).
  * Regex and NER for semi-structured/free-form data (e.g., “Jane Doe,” “Dr. McCulloch”).
* **Reinjection:** Map tokens back to original values using stored lookup for specific flows.

### 4. **Stateless Lambda Operation**

* All per-request context (e.g., which fields/entities to tokenize, mapping keys) must be passed as part of the request or retrievable from config storage (e.g., SSM Parameter Store).

---

## **Non-Functional Requirements**

* **Security:**

  * All mapping storage must be encrypted at rest and in transit.
  * Tokens must not be guessable/reversible without access to mapping store.
  * Service must support per-tenant or per-domain isolation (multi-tenant safe).
* **Performance:**

  * Must handle \~10–100 requests/sec with sub-second latency.
  * Must scale with AWS Lambda’s automatic scaling.
* **Auditing/Logging:**

  * All anonymization/deanonymization requests are logged (excluding sensitive payload).
  * Audit logs must not contain raw PII.
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

```text
Jane Doe<my.email@emailhost.com>
Mon, Jan 01, 12:45 PM
to me

Hello,

I have a question for Dr. McCulloch regarding my pms-progesterone prescription. During our last appt, she mentioned the option of switching to the oral compounded version with the help of an MD she knows who could write the prescription. I am just completing my first 14 day course of the vaginal suppositories, and while it is going well, I am hoping to switch to the oral version before my next cycle of the prescription (roughly in 21 days).

I was wondering if she is comfortable sharing the name of this doctor so I can start with the oral version next cycle, or if she would rather me book an appointment.

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
* **Storage:** DynamoDB (preferred for low-latency key/value mapping).
* **Deployment:** AWS Lambda + API Gateway; configuration in S3 or SSM.
* **Access:** Auth via AWS IAM or JWT (depending on environment).

---

## **Edge Cases & Open Questions**

* What’s the retention policy for mapping tables?
* Should we support batch/bulk anonymization?
* Do we need audit “reversal” (e.g., to revoke or invalidate tokens)?
* Multi-tenant: field/entity mapping and token namespace per-tenant?
* API Gateway: private (VPC) or public endpoint?

---

**Next Steps:**

* Confirm field/entity extraction spec and sample payloads for each integration.
* Decide on retention/isolation policy for mapping storage.
* Finalize config interface (S3/SSM/inline).
* Prototype with spaCy and evaluate Lambda deployment size/performance.

---

Let me know if you need a separate “Glossary” section, further email scenarios, or implementation samples!
