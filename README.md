# LLM-Based-Product-Recommendation-System-1.0

## Overview
This project implements a FastAPI-based product recommendation system using `distilgpt2`, a lightweight GPT-2 variant, and a SQLite database (`recommendation.db`). It supports user creation, JWT authentication, and personalized product recommendations via a RAG pipeline.

## Features

- **Database**: SQLite with 3665 products, 4339 users, 397924 feedback entries.
- **Endpoints**: `/users/` (create user), `/token` (authenticate), `/recommend/` (generate recommendations).
- **RAG Pipeline**: Adapts `distilgpt2` for recommendations, tested via `test_llm.py`.
- **Authentication**: JWT-based with password hashing.
- **Monitoring**: Logs to `recommendation_system.log`.
- **Documentation**: Docstrings in all Python files; `proof_of_work.md` with endpoint tests.

## Setup

1. Clone the repository:
   ```bash
   git clone (repo link)
   cd recommendation-system
2. Create and activate a virtual environment:
   # Windows: venv\Scripts\activate
3. Install dependencies:
  pip install -r requirements.txt
4. Run the FastAPI server:
    uvicorn main:app --reload
5. Test endpoints (see proof_of_work.md).
   
## Files

main.py: FastAPI application.
api.py: User and recommendation endpoints.
auth.py: Authentication endpoint.
database.py: SQLAlchemy setup.
models.py: Database models.
llm_engine.py: RAG pipeline.
test_llm.py: RAG pipeline tests.
proof_of_work.md: Documentation with endpoint tests.

## Notes

1. Uses distilgpt2 for efficiency, aligned with GPT-2.
2. RAG pipeline ensures effective recommendations.
3. Caching and feedback endpoints planned for future work.
   
#MANVI CHAND
EOF
