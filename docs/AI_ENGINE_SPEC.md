# 07_AI_ENGINE_SPEC.md (Stub)

> **Status:** Stub for Milestone 5. Prompts live in `app/ai/prompts/`, not in route handlers.

---

## Principles

1. LLM performs structured analysis using rubrics — it does **not** autonomously grade.
2. All AI outputs must be **valid JSON** matching Pydantic schemas.
3. Invalid responses are rejected; nothing persisted until validated.
4. Frontend never calls OpenAI; only `AIEvaluationService` and `RubricService`.

---

## Provider Abstraction

```text
AIEvaluationService → AIProvider (protocol) → OpenAIProvider
```

Environment: `OPENAI_API_KEY`, `OPENAI_MODEL` (default `gpt-4o-mini`)

---

## Evaluation Response Schema

```json
{
  "overall_score": 81,
  "mastery_level": "PROFICIENT",
  "confidence_level": "HIGH",
  "strengths": ["string"],
  "weaknesses": ["string"],
  "misconceptions": ["string"],
  "recommendations": ["string"],
  "concept_scores": [{ "concept_id": "string", "score": 0, "status": "PROFICIENT" }]
}
```

`mastery_level`: `BEGINNER | DEVELOPING | PROFICIENT | ADVANCED | EXPERT`  
`confidence_level`: `LOW | MEDIUM | HIGH`

---

## Rubric Generation Response Schema

```json
{
  "concepts": [{ "id": "string", "name": "string", "description": "string" }],
  "evaluation_rules": [{ "criterion": "string", "weight": 1 }],
  "common_misconceptions": [{ "concept": "string", "misconception": "string" }]
}
```

---

## Pipeline (Milestone 5)

```text
Assessment + Rubric + Topic → PromptBuilder → OpenAI → JSON parse → Pydantic validate
  → EvaluationRepository → RecommendationService → ReportService → KnowledgeGraphService
```

---

## Error Handling

- Timeout / API failure → `AI_ENGINE_ERROR` (500)
- Invalid JSON / schema → retry once, then `AI_ENGINE_ERROR`
- Assessment status → `FAILED`

---

## Testing

- Mock `AIProvider` in unit tests
- Never call live OpenAI in CI

---

## Prompt Files (Milestone 5)

```text
app/ai/prompts/
├── evaluate_answer.txt
├── generate_rubric.txt
└── system_educator.txt
```
