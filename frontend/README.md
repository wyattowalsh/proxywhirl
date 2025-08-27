# ProxyWhirl Frontend

Vite + React + TypeScript SPA for the ProxyWhirl Command Center.

---

## ## Technology Stack

* **Core & Build:** Vite, React 19+, TypeScript
* **Routing:** React Router
* **State Management:**
    * **Server State:** TanStack Query
    * **Client State:** Zustand
* **API Communication:** Axios, Socket.IO Client
* **Styling & UI:**
    * **CSS:** Tailwind CSS 4
    * **Components:** Shadcn/ui
* **Data Visualization & Tables:**
    * **Charts:** Recharts
    * **Tables:** TanStack Table (Headless)
* **Animations:** Framer Motion
* **Testing:** Vitest, React Testing Library
* **Linting & Formatting:** ESLint, Prettier

---

## ## Setup

1.  **Install dependencies:**
    ```zsh
    pnpm install
    ```

2.  **Configure environment:**
    Copy the `.env.example` file to `.env.local` and set the API base URL.
    ```zsh
    cp .env.example .env.local
    ```

3.  **Run the development server:**
    ```zsh
    pnpm dev
    ```
    The application will be available at `http://localhost:5173`.

---

## ## Available Scripts

* `pnpm dev`: Starts the development server with HMR.
* `pnpm build`: Compiles and bundles the app for production.
* `pnpm test`: Runs the test suite using Vitest.
* `pnpm lint`: Lints all source files with ESLint.
* `pnpm preview`: Serves the production build locally for inspection.

---

## ## Adding UI Components

This project uses **shadcn-ui**. Add new, unstyled components to your project using the CLI. These components are then fully customizable with Tailwind CSS.

```zsh
pnpm dlx shadcn-ui@latest add button
```