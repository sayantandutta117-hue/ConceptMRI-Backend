# 05_DATABASE_DESIGN.md (Stub)

> **Status:** Stub derived from Backend-specs, api-contracts, and Frontend-spec data contracts.  
> **Authoritative for Milestone 1 implementation** until official doc is provided.

---

## Enums

```text
UserRole:     student | teacher | admin
UserStatus:   ACTIVE | INACTIVE | SUSPENDED
Difficulty:   EASY | MEDIUM | HARD
AssessmentStatus: PENDING_EVALUATION | PROCESSING | COMPLETED | REPORT_AVAILABLE | FAILED
MasteryLevel: BEGINNER | DEVELOPING | PROFICIENT | ADVANCED | EXPERT
ConfidenceLevel: LOW | MEDIUM | HIGH
RecommendationPriority: HIGH | MEDIUM | LOW
RubricStatus: CREATED | ACTIVE | ARCHIVED
```

---

## Tables

### users

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| email | VARCHAR UNIQUE NOT NULL | indexed |
| password_hash | VARCHAR NOT NULL | bcrypt |
| name | VARCHAR NOT NULL | |
| role | ENUM(UserRole) NOT NULL | indexed |
| status | ENUM(UserStatus) DEFAULT ACTIVE | |
| institution | VARCHAR NULL | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### students (profile extension)

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| user_id | UUID FK → users UNIQUE | |
| class_id | UUID FK → classes NULL | MVP: nullable |
| learning_streak | INT DEFAULT 0 | |
| created_at | TIMESTAMPTZ | |

### teachers (profile extension)

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| user_id | UUID FK → users UNIQUE | |
| created_at | TIMESTAMPTZ | |

### classes (MVP minimal)

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| name | VARCHAR NOT NULL | |
| teacher_id | UUID FK → teachers | indexed |
| created_at | TIMESTAMPTZ | |

### topics

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| subject | VARCHAR NOT NULL | indexed |
| topic_name | VARCHAR NOT NULL | |
| difficulty | ENUM(Difficulty) | indexed |
| description | TEXT | |
| learning_objectives | JSONB | array of strings |
| prerequisites | JSONB | array of topic UUIDs or concept ids |
| is_archived | BOOLEAN DEFAULT false | soft delete |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### rubrics

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| topic_id | UUID FK → topics | indexed |
| concepts | JSONB | |
| evaluation_rules | JSONB | |
| common_misconceptions | JSONB | |
| status | ENUM(RubricStatus) | |
| created_at | TIMESTAMPTZ | |

### assessments

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| student_id | UUID FK → students | indexed |
| topic_id | UUID FK → topics | indexed |
| answer | TEXT NOT NULL | 20-5000 chars |
| status | ENUM(AssessmentStatus) | indexed |
| submitted_at | TIMESTAMPTZ | |
| completed_at | TIMESTAMPTZ NULL | |
| created_at | TIMESTAMPTZ | |

### evaluations

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| assessment_id | UUID FK → assessments UNIQUE | |
| overall_score | INT | 0-100 |
| mastery_level | ENUM(MasteryLevel) | |
| confidence_level | ENUM(ConfidenceLevel) | |
| strengths | JSONB | array |
| weaknesses | JSONB | array |
| misconceptions | JSONB | array |
| raw_ai_response | JSONB NULL | debug only, omit from API |
| created_at | TIMESTAMPTZ | |

### mri_reports

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| evaluation_id | UUID FK → evaluations UNIQUE | |
| overall_score | INT | |
| mastery_level | ENUM(MasteryLevel) | |
| teacher_summary | TEXT | |
| student_summary | TEXT | |
| strengths | JSONB | |
| weaknesses | JSONB | |
| misconceptions | JSONB | |
| created_at | TIMESTAMPTZ | immutable after create |

### recommendations

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| student_id | UUID FK → students | indexed |
| evaluation_id | UUID FK → evaluations NULL | |
| class_id | UUID FK → classes NULL | teaching recs |
| concept | VARCHAR | |
| description | TEXT | |
| reason | TEXT | |
| suggested_action | TEXT | |
| priority | ENUM(RecommendationPriority) | |
| created_at | TIMESTAMPTZ | |

### knowledge_graph_nodes

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| student_id | UUID FK → students | composite unique with concept_id |
| concept_id | VARCHAR | e.g. "recursion" |
| status | ENUM(MasteryLevel) | |
| confidence | ENUM(ConfidenceLevel) NULL | |
| updated_at | TIMESTAMPTZ | |

### knowledge_graph_edges

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| student_id | UUID FK → students | |
| from_concept | VARCHAR | |
| to_concept | VARCHAR | prerequisite edge |

---

## Relationships

```text
users 1──1 students | teachers (by role)
teachers 1──* classes
classes 1──* students
topics 1──* rubrics
students 1──* assessments *──1 topics
assessments 1──1 evaluations 1──1 mri_reports
evaluations 1──* recommendations
students 1──* knowledge_graph_nodes
students 1──* knowledge_graph_edges
```

---

## Indexes

- `users(email)` UNIQUE
- `users(role)`
- `students(user_id)` UNIQUE
- `students(class_id)`
- `teachers(user_id)` UNIQUE
- `topics(subject, difficulty)`
- `rubrics(topic_id)`
- `assessments(student_id, status)`
- `assessments(topic_id)`
- `evaluations(assessment_id)` UNIQUE
- `mri_reports(evaluation_id)` UNIQUE
- `recommendations(student_id, priority)`
- `knowledge_graph_nodes(student_id, concept_id)` UNIQUE

---

## Seed Data (Milestone 1)

- 1 admin, 1 teacher, 2 students (demo passwords via env)
- 5+ topics across Python subject
- 1 class linking teacher + students
