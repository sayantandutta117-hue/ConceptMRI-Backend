# API Alignment — Frontend Expectations → Backend Implementation

> Maps every endpoint referenced in Frontend-spec and Backend-specs `api-contracts.md`.  
> **Source of truth for response shape:** `Backend-specs/api-contracts.md` + standardized envelope.

Legend: ✅ Defined in api-contracts | 🔶 Frontend expects, backend must implement | ⏳ Milestone

---

## Authentication

| Method | Path | Auth | Milestone | Status |
| ------ | ---- | ---- | --------- | ------ |
| POST | `/api/v1/auth/login` | Public | M3 | 🔶 |
| GET | `/api/v1/auth/me` | Bearer | M3 | 🔶 |
| POST | `/api/v1/auth/logout` | Bearer | M3 | 🔶 |

**Login request:**
```json
{ "email": "string", "password": "string" }
```

**Login response `data`:**
```json
{ "access_token": "string", "token_type": "bearer", "user": { "id", "email", "name", "role" } }
```

---

## Users

| Method | Path | Roles | Milestone |
| ------ | ---- | ----- | --------- |
| GET | `/api/v1/users/me` | All | M3 |
| PATCH | `/api/v1/users/me` | All | M3 |
| GET | `/api/v1/admin/users` | Admin | M6 |
| GET | `/api/v1/admin/users/{id}` | Admin | M6 |
| PATCH | `/api/v1/admin/users/{id}` | Admin | M6 |

---

## Topics

| Method | Path | Roles | Milestone |
| ------ | ---- | ----- | --------- |
| GET | `/api/v1/topics` | Student, Teacher, Admin | M4 |
| GET | `/api/v1/topics/{topicId}` | Student, Teacher, Admin | M4 |
| POST | `/api/v1/topics` | Admin | M6 |
| PATCH | `/api/v1/topics/{topicId}` | Admin | M6 |

Query params: `subject`, `difficulty`, `page`, `limit`, `sort`

---

## Rubrics

| Method | Path | Roles | Milestone |
| ------ | ---- | ----- | --------- |
| POST | `/api/v1/rubrics` | Admin, Teacher | M4 |
| GET | `/api/v1/rubrics/{topicId}` | Teacher, Admin | M4 |
| GET | `/api/v1/rubrics` | Admin | M6 |

**Generate rubric request:** `{ "topic_id": "uuid" }`

---

## Assessments & Evaluations

| Method | Path | Roles | Milestone |
| ------ | ---- | ----- | --------- |
| POST | `/api/v1/assessments` | Student | M5 |
| GET | `/api/v1/assessments/{assessmentId}` | Student, Teacher, Admin | M5 |
| GET | `/api/v1/assessments/student/{studentId}` | Student (own), Teacher, Admin | M5 |
| POST | `/api/v1/evaluations` | Internal / Backend | M5 |
| GET | `/api/v1/evaluations/{evaluationId}` | Student, Teacher, Admin | M5 |
| GET | `/api/v1/reports/{reportId}` | Student, Teacher, Admin | M5 |

**Submit assessment request:**
```json
{
  "student_id": "uuid",
  "topic_id": "uuid",
  "answer": "string (20-5000 chars)"
}
```

**Submit assessment response `data`:**
```json
{ "assessment_id": "uuid", "status": "PENDING_EVALUATION" }
```

**Evaluation trigger request:** `{ "assessment_id": "uuid" }`

**MRI report `data` fields:** `overall_score`, `mastery_level`, `teacher_summary`, `student_summary`, `strengths`, `weaknesses`, `misconceptions`, `recommendations`

---

## Dashboards

| Method | Path | Notes | Milestone |
| ------ | ---- | ----- | --------- |
| GET | `/api/v1/dashboard/student/{studentId}` | ✅ api-contracts | M6 |
| GET | `/api/v1/dashboard/student` | 🔶 Frontend-spec alias — uses JWT `sub` | M6 |
| GET | `/api/v1/dashboard/teacher/{teacherId}` | ✅ | M6 |
| GET | `/api/v1/dashboard/teacher` | 🔶 JWT alias | M6 |
| GET | `/api/v1/dashboard/admin` | 🔶 Frontend-spec | M6 |

**Student dashboard `data` includes:** `student`, `overall_score`, `mastery_level`, `knowledge_graph`, `recent_assessments`, `recommendations`

**Teacher dashboard `data` includes:** `class_average`, `student_count`, `weak_topics`, `heatmap`, `recommendations`

---

## Analytics

| Method | Path | Milestone |
| ------ | ---- | --------- |
| GET | `/api/v1/analytics/student/{studentId}` | M6 |
| GET | `/api/v1/analytics/student` | M6 (JWT alias) |
| GET | `/api/v1/analytics/class/{classId}` | M6 |
| GET | `/api/v1/analytics/platform` | M6 |
| GET | `/api/v1/analytics/topics` | M6 |
| GET | `/api/v1/admin/analytics` | M6 |

**Knowledge graph standard shape (embedded or standalone):**
```json
{
  "nodes": [{ "id": "string", "status": "PROFICIENT" }],
  "edges": [{ "from": "string", "to": "string" }]
}
```

| GET | `/api/v1/knowledge-graph` | M6 | Student UI standalone endpoint |

---

## Recommendations

| Method | Path | Milestone |
| ------ | ---- | --------- |
| GET | `/api/v1/recommendations/student/{studentId}` | M6 |
| GET | `/api/v1/recommendations/class/{classId}` | M6 |

---

## Admin Operations

| Method | Path | Milestone |
| ------ | ---- | --------- |
| GET | `/api/v1/admin/assessments` | M6 |
| GET | `/api/v1/admin/ai/health` | M6 |
| GET | `/api/v1/students/{id}` | M6 |
| GET | `/api/v1/reports/student/{id}` | M6 |
| GET | `/api/v1/teacher/insights` | M6 |

---

## Standard Envelope (All Endpoints)

**Success:**
```json
{
  "success": true,
  "message": "Human readable message.",
  "data": {},
  "timestamp": "2026-08-02T10:30:00Z"
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable message.",
    "details": []
  },
  "timestamp": "2026-08-02T10:31:00Z"
}
```

**Error codes:** `VALIDATION_ERROR`, `RESOURCE_NOT_FOUND`, `UNAUTHORIZED`, `FORBIDDEN`, `AI_ENGINE_ERROR`, `DATABASE_ERROR`, `INTERNAL_SERVER_ERROR`

---

## Pagination (List Endpoints)

```json
{
  "success": true,
  "data": [],
  "pagination": { "page": 1, "limit": 20, "total": 125, "pages": 7 },
  "timestamp": "..."
}
```

---

## Authorization Matrix (Enforced in Service Layer)

| Resource | Student | Teacher | Admin |
| -------- | ------- | ------- | ----- |
| Own assessments/reports | ✅ | ❌ | ✅ all |
| Class analytics | ❌ | ✅ own classes | ✅ |
| Rubrics | ❌ | ✅ read | ✅ |
| User management | ❌ | ❌ | ✅ |
