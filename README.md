# TATA ELXSI MOCK API - Backend

FastAPI backend issuing JWT tokens and returning responses tailored to each user's subscription package.

## Running and Connectivity

- Backend Docs (OpenAPI): typically at https://<backend-host>:3001/docs
- Frontend (React): ensure it points to the correct backend base URL

### Required environment

Copy `backend/.env.example` to `backend/.env` and fill in values. At minimum:
- Set CORS_ORIGINS to the exact frontend origin (scheme + host + optional port), e.g.:
  CORS_ORIGINS=https://vscode-internal-27635-beta.beta01.cloud.kavia.ai:4000

The backend automatically loads `.env` and will also consider FRONTEND_ORIGIN, FRONTEND_URL, SITE_URL, PUBLIC_SITE_URL, REACT_APP_SITE_URL, or VITE_SITE_URL if CORS_ORIGINS is not set.

### Frontend configuration

In the React app, set the base URL for API calls:
- REACT_APP_BACKEND_URL=https://<backend-host>:3001

For the current preview environment:
- Frontend URL: https://vscode-internal-27635-beta.beta01.cloud.kavia.ai:4000
- Backend URL:  https://vscode-internal-27635-beta.beta01.cloud.kavia.ai:3001

Ensure REACT_APP_BACKEND_URL matches the backend URL above; otherwise, the frontend will fail to reach the backend.

### Common connectivity issues

- NetworkError: Failed to reach the backend
  - Verify REACT_APP_BACKEND_URL is set to the correct host/port (avoid mixing 23420 vs 27635 hostnames)
  - Ensure backend is running and accessible at the expected URL
  - Set backend CORS_ORIGINS (or one of the fallbacks) to include the exact frontend origin
  - Avoid mixed content (always use https when the site is https)
  - TLS/hostname mismatches: make sure both URLs share the same base host if required by your environment

### Development notes

- Public API routes include:
  - POST /auth/signup
  - POST /auth/login
  - GET  /dashboard/me
  - GET  /api/content
  - GET  /account/plan
  - PUT  /account/plan

- To regenerate OpenAPI JSON under backend/interfaces/openapi.json:
  python -m src.api.generate_openapi