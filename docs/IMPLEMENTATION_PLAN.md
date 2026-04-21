# Debate AI - Architecture & Implementation Plan

## Overview
Agentic AI research-paper debate/learning tool using LangChain, OpenAI, RAG and Vector Databases. Pits two LLMs against each other to debate topics from user-uploaded research papers.

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│  FastAPI    │────▶│   RAG       │
│   (React)   │     │   Backend   │     │   Pipeline  │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                          │                    │
              ┌───────────┼────────────┐       │
              ▼           ▼            ▼       ▼
         ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
         │ Topic  │ │ Debate   │ │ Debate   │ │ Weaviate │
         │ Gen    │ │ Agent 1  │ │ Agent 2  │ │ Vector   │
         │ (LLM)  │ │ (Pro)    │ │ (Con)    │ │ Store    │
         └────────┘ └──────────┘ └──────────┘ └──────────┘
              │           │            │
              └───────────┼────────────┘
                          ▼
                   ┌──────────┐
                   │ Manager  │
                   │ Agent    │
                   └──────────┘
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| LLM | OpenAI (GPT-4o/GPT-4o-mini) |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | Weaviate |
| Framework | LangChain |
| PDF Processing | PyPDFLoader |

---

## Design Decisions

### 1. LLM Provider: OpenAI
- Reliable, production-ready
- Good citation generation
- Fast response times

### 2. Vector Database: Weaviate
- Production-ready, cloud-native
- Easy persistence
- GoodLangChain integration

### 3. Debate Flow: Sequential
- Manager orchestrates turn-by-turn
- Pro opens → Con responds → Rebuttals alternate
- Clear winner determination

### 4. Citations: Required
- Every claim must cite paper source
- Citation format: `[Section X, Page Y]`
- Manager validates citations

---

## Database Schema (Weaviate)

### DebateSession
| Property | Type | Description |
|----------|------|-------------|
| session_id | string | Unique identifier |
| paper_content | text | Full paper text |
| topic | string | Selected debate topic |
| pro_premise | text | Pro argument premise |
| con_premise | text | Con argument premise |
| status | string | pending/active/completed |
| created_at | datetime | Creation timestamp |

### DebateTurn
| Property | Type | Description |
|----------|------|-------------|
| session_id | string | Link to session |
| turn_number | int | Turn order |
| agent_role | string | pro/con/manager |
| content | text | Agent response |
| citations | string[] | Source citations |
| timestamp | datetime | Turn timestamp |

---

## Agent System

### 1. Topic Generator Agent
- **Input**: Paper content
- **Output**: 3 debate topics with Pro/Con premises
- **Model**: GPT-4o-mini (cost-effective)

### 2. Debate Agent (Pro)
- **Role**: Argue FOR the motion
- **Tools**: RAG retriever
- **Constraint**: Must cite sources

### 3. Debate Agent (Con)
- **Role**: Argue AGAINST the motion
- **Tools**: RAG retriever
- **Constraint**: Must cite sources

### 4. Manager Agent
- Controls debate flow
- Evaluates turn quality
- Ends debate (max 6-8 rounds or consensus)
- Generates final summary

---

## Debate Flow (Sequential)

```
1. User uploads paper → RAG stores in Weaviate
2. User selects topic OR auto-generate topics
3. Manager Agent starts:
   - Turn 1: Pro opening (cite evidence)
   - Turn 2: Con opening (cite evidence)
   - Turn 3: Pro rebuttal
   - Turn 4: Con rebuttal
   ... (max 6-8 rounds)
4. Manager summarizes outcome
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload PDF, process, store |
| `/topics` | POST | Generate debate topics |
| `/debate/start` | POST | Start new debate |
| `/debate/next` | POST | Get next turn |
| `/debate/status` | GET | Get debate state |
| `/debate/summary` | GET | Get final summary |

---

## File Structure

```
server/
├── main.py                    # FastAPI app
├── config.py                  # Environment variables
├── constants.py               
├── agents/
│   ├── __init__.py
│   ├── base.py               # Base agent
│   ├── topic_generator.py    # Topic extraction
│   ├── debate_agent.py       # Pro/Con agents
│   └── manager.py            # Orchestration
├── rag/
│   ├── __init__.py
│   ├── pipeline.py           # PDF → Weaviate
│   ├── retriever.py          # Retrieval + citations
│   └── weaviate_client.py    # Weaviate connection
├── api/
│   ├── __init__.py
│   ├── upload.py             # File upload
│   ├── debate.py             # Debate endpoints
│   └── models.py             # Pydantic models
└── services/
    ├── __init__.py
    └── debate_service.py     # Business logic
```

---

## Quality Metrics

| Metric | Description |
|--------|-------------|
| Citation Rate | % of claims with valid citations |
| Rebuttal Quality | Addresses opponent's specific points |
| Convergence | When both agents agree/repeat |

---

## Implementation Priority

1. config.py + RAG pipeline
2. Topic Generator agent
3. Debate Agent base
4. Manager Agent
5. API endpoints
6. Streaming support
