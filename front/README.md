# Frontend (Vue.js 3 Application)

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).

## API Integration

-   **API Service Layer**: API calls to the backend are organized in `src/services/api/`. Each resource (e.g., auth, content, course) has its own file (`auth.ts`, `content.ts`, etc.) containing typed functions for API interactions.
-   **Axios Configuration**: A shared Axios instance is configured in `src/services/api/index.ts`.
    -   It uses a `baseURL` pointing to the backend API (`http://localhost:8000/api/v1`).
    -   An interceptor automatically attaches JWT tokens from `localStorage` to outgoing requests.
    -   A response interceptor handles global API errors, including 401 Unauthorized errors (which currently triggers a logout and redirect to login).
-   **Type Definitions**: TypeScript interfaces for API request payloads and responses are defined in `src/types/api/`, mirroring the backend's Pydantic schemas.

## Running the Frontend

(Assuming standard commands, add actual commands if they were previously in this README)
```bash
npm install
npm run dev
```

Make sure the backend server is running and accessible at the configured API URL (default `http://localhost:8000`).

## Current Development Status

-   The backend FastAPI application is largely complete, including database models, API endpoints for all major features, and an authentication system. The initial database migration script has been generated.
-   The frontend has a structured API service layer for communicating with the backend.
-   **Note on Pinia Stores and Component Integration**: The process of updating Pinia stores (`src/stores/*.ts`) to use the new API services and subsequently updating Vue components to use these stores was **not completed** due to persistent technical issues with the development environment's file writing tools. Therefore, the existing Pinia stores and Vue components still use their original mock data or simulated API calls and do not yet reflect live backend integration. This part will require manual completion.
