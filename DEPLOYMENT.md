# Deployment Guide: NEWSLENS.AI 2.0

## Docker Compose (Local & Production Simulation)
1. Install Docker Desktop.
2. Run `docker-compose up --build -d` in this directory.
3. The Flask API and the Frontend dashboard will be natively mapped on `http://localhost:5000`.

## Render.com (Backend Web Service)
1. Bind your GitHub repository to Render.
2. Create a **New Web Service**.
3. Select Docker as the Runtime.
4. Set up the Environment Variables:
   - `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`, `D_ID_API_KEY`, `NEWSAPI_KEY`
5. Deploy.
