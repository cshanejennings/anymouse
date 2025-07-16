# **Anymouse Edge and Corner Case Examples**

This document provides example inputs and expected anonymized outputs to clarify how the service should behave in non-obvious situations.

---

## **1. Structured Input with Overlapping Field Names**

**Input:**

```json
{
  "payload": {
    "patient_name": "Jane Doe",
    "referrer_name": "Dr. John Smith",
    "appointment": {
      "doctor": "Dr. Fiona McCulloch"
    }
  },
  "config": {
    "fields": ["patient_name", "referrer_name", "appointment.doctor"]
  }
}
```

**Expected Output:**

```json
{
  "message": "{ \"patient_name\": \"[name1]\", \"referrer_name\": \"[name2]\", \"appointment\": { \"doctor\": \"[name3]\" } }",
  "tokens": {
    "name1": "Jane Doe",
    "name2": "Dr. John Smith",
    "name3": "Dr. Fiona McCulloch"
  },
  "fields": ["patient_name", "referrer_name", "appointment.doctor"]
}
```

---

## **2. Free-form Email with Multiple Distinct Names and Entities**

**Input:**

```text
From: Jane Doe <jane.doe@email.com>
To: Dr. Fiona McCulloch <fiona@clinic.com>
Subject: Referral

Hello Dr. McCulloch,

Dr. John Smith suggested I reach out to you. My name is Jane Doe and I'd like to book an appointment.

Thank you,
Jane Doe
```

**Expected Output:**

```json
{
  "message": "From: [name1] <jane.doe@email.com>\nTo: [name2] <fiona@clinic.com>\nSubject: Referral\n\nHello [name2],\n\n[name3] suggested I reach out to you. My name is [name1] and I'd like to book an appointment.\n\nThank you,\n[name1]",
  "tokens": {
    "name1": "Jane Doe",
    "name2": "Dr. Fiona McCulloch",
    "name3": "Dr. John Smith"
  },
  "fields": ["PERSON"]
}
```

---

## **3. Nested/Repeating Entities**

**Input:**

```text
Family Members:
- John Doe (Father)
- Jane Doe (Mother)
- John Doe Jr. (Son)
```

**Expected Output:**

```json
{
  "message": "Family Members:\n- [name1] (Father)\n- [name2] (Mother)\n- [name3] (Son)",
  "tokens": {
    "name1": "John Doe",
    "name2": "Jane Doe",
    "name3": "John Doe Jr."
  },
  "fields": ["PERSON"]
}
```

*Note: Handles repeated first/last names as distinct entities.*

---

## **4. Entity in Multiple Forms (Title, Abbreviation, Signature Block)**

**Input:**

```text
To Whom It May Concern,

My physician, Dr. Fiona McCulloch (F. McCulloch), referred me for genetic testing.

Best,
Fiona
```

**Expected Output:**

```json
{
  "message": "To Whom It May Concern,\n\nMy physician, [name1] ([name2]), referred me for genetic testing.\n\nBest,\n[name3]",
  "tokens": {
    "name1": "Dr. Fiona McCulloch",
    "name2": "F. McCulloch",
    "name3": "Fiona"
  },
  "fields": ["PERSON"]
}
```

*Note: Each detected name, even if potentially the same person, is tokenized individually unless context resolution is implemented.*

---

## **5. Ambiguous Name-like Text (False Positive Test)**

**Input:**

```text
The patient was prescribed Warfarin.
```

**Expected Output:**

```json
{
  "message": "The patient was prescribed Warfarin.",
  "tokens": {},
  "fields": ["PERSON"]
}
```

*Note: “Warfarin” is a drug name, not a person—should **not** be replaced.*

---

## **6. Embedded Names in Quoted Text / Replies**

**Input:**

```text
On Jan 1, 2024, at 12:45 PM, Dr. John Smith <john@clinic.com> wrote:
> Please follow up with Jane Doe.

Hi Dr. Smith, thank you for your message. I've reached out to Jane.
```

**Expected Output:**

```json
{
  "message": "On Jan 1, 2024, at 12:45 PM, [name1] <john@clinic.com> wrote:\n> Please follow up with [name2].\n\nHi [name3], thank you for your message. I've reached out to [name2].",
  "tokens": {
    "name1": "Dr. John Smith",
    "name2": "Jane Doe",
    "name3": "Dr. Smith"
  },
  "fields": ["PERSON"]
}
```

*Note: Handles names inside quoted text, as well as short forms (“Dr. Smith”).*

---

## **7. No Entities Detected**

**Input:**

```text
No names appear in this message.
```

**Expected Output:**

```json
{
  "message": "No names appear in this message.",
  "tokens": {},
  "fields": ["PERSON"]
}
```

---

## **8. Entities Mixed with Contact Info**

**Input:**

```text
Contact: Dr. Fiona McCulloch (fiona@clinic.com, 555-555-5555)
```

**Expected Output:**

```json
{
  "message": "Contact: [name1] (fiona@clinic.com, 555-555-5555)",
  "tokens": {
    "name1": "Dr. Fiona McCulloch"
  },
  "fields": ["PERSON"]
}
```

---

## **9. Overlapping Entity Types (Optional, if Supported)**

**Input:**

```text
The patient saw Dr. John Smith at Sunnybrook Hospital in Toronto on Jan 1, 2024.
```

**Expected Output:**

```json
{
  "message": "The patient saw [name1] at [org1] in [loc1] on [date1].",
  "tokens": {
    "name1": "Dr. John Smith",
    "org1": "Sunnybrook Hospital",
    "loc1": "Toronto",
    "date1": "Jan 1, 2024"
  },
  "fields": ["PERSON", "ORG", "GPE", "DATE"]
}
```

*Note: Shows support for multiple entity types if your implementation includes them.*
