# **Requirements Document: Anonymization Service (AWS Lambda)**

[See the discussion link](https://chatgpt.com/c/687812c9-c764-800e-b8c9-4c4cf9949ad6)

## **Purpose**

Provide a stateless microservice to anonymize and deanonymize sensitive data passing through administrative/accounting integrations (Jane EMR, Shopify, QBO, etc.), via tokenization and lookup, suitable for regulatory compliance and minimum patient identification risk.

---

## **Functional Requirements**

### 1. **Tokenization / Anonymization**

* **Input:** Raw data payloads (JSON/CSV) containing potentially identifying fields.
* **Process:**

  * Extract target fields (e.g., patient name, email, address, invoice IDs, etc.) using field config/regex.
  * Replace these fields with unique, deterministic tokens (e.g., UUIDv4, hash, or salted hash).
  * Store a mapping (token → real value) in a secure, isolated data store (e.g., DynamoDB, encrypted S3, or RDS).
  * Non-identifying fields pass through unchanged.
* **Output:** Anonymized payload, suitable for downstream integration.

### 2. **Lookup / Deanonymization**

* **Input:** Payloads with tokens in place of real values.
* **Process:**

  * Identify token fields (matching token pattern/namespace).
  * Lookup token mappings and replace with the original value.
* **Output:** Deanonymized payload (e.g., for internal audit, support).

### 3. **Pre/Post-Processing Hooks**

* **Extraction:** Configurable logic to identify and extract fields for anonymization, including support for:

  * Field mappings (simple: “patient\_name” → tokenize; complex: nested/array fields).
  * Regex-based matching for semi-structured data.
* **Reinjection:** Map tokens back to original values using stored lookup for specific flows.

### 4. **Stateless Lambda Operation**

* All per-request context (e.g., which fields to tokenize, mapping keys) must be passed as part of the request or retrievable from config storage (e.g., SSM Parameter Store).

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

  * Field mappings and regexes are externally configurable (JSON, YAML, or fetched from S3/SSM).

---

## **API Design**

### **Endpoints**

* `POST /anonymize`

  * Input: `{ payload: <data>, config: <optional override> }`
  * Output: `{ anonymized: <payload>, mapping_keys: <optional> }`
* `POST /deanonymize`

  * Input: `{ payload: <data>, mapping_keys: <optional> }`
  * Output: `{ deanonymized: <payload> }`
* `POST /config/test`

  * (Validate/test a new extraction/config payload.)

### **Payload Example**

#### Anonymization Request

```json
{
  "payload": {
    "patient_name": "Jane Doe",
    "email": "jane@example.com",
    "visit": {
      "date": "2024-01-01",
      "id": "abc-123"
    }
  },
  "config": {
    "fields": ["patient_name", "email", "visit.id"]
  }
}
```

#### Anonymized Response

```json
{
  "anonymized": {
    "patient_name": "token:8ac0...",
    "email": "token:1d3c...",
    "visit": {
      "date": "2024-01-01",
      "id": "token:ab9a..."
    }
  }
}
```

---

## **Implementation Constraints**

* **Language:** Node.js or Python (best AWS Lambda support).
* **Storage:** DynamoDB (preferred for low-latency key/value mapping).
* **Deployment:** AWS Lambda + API Gateway; configuration in S3 or SSM.
* **Access:** Auth via AWS IAM or JWT (depending on environment).

---

## **Edge Cases & Open Questions**

* What’s the retention policy for mapping tables?
* Should we support batch/bulk anonymization?
* Do we need audit “reversal” (e.g., to revoke or invalidate tokens)?
* Multi-tenant: field mapping and token namespace per-tenant?
* API Gateway: private (VPC) or public endpoint?

---

**Next Steps:**

* Confirm field extraction spec and sample payloads for each integration.
* Decide on retention/isolation policy for mapping storage.
* Finalize config interface (S3/SSM/inline).
