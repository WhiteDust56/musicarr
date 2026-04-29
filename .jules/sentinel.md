## 2024-04-29 - Overly Permissive CORS Configuration
**Vulnerability:** The FastAPI application used `allow_origins=["*"]` along with `allow_credentials=True`.
**Learning:** This combination allows any website to make cross-origin requests with the user's credentials (cookies, auth headers), potentially leading to data exposure or CSRF.
**Prevention:** Always restrict `allow_origins` to specific trusted domains, especially when `allow_credentials=True` is required. Use environment variables to make origins configurable per environment.