# Project BishopForge – Frontend

This is the **frontend client** for Project BishopForge:  
A modular, testable chess UI built with **Vite**, **Vanilla JavaScript**, and **chess.js**.

The frontend is responsible for:

- Rendering the chessboard
- Applying moves and validations
- Managing optional features:
  - Highlight legal moves
  - Undo/takeback
  - Forced SAN moves (study mode)
- Communicating with the optional FastAPI backend

---

## 🔧 Requirements

- Node.js **18+**
- npm **9+**

You can verify with:

node -v
npm -v

yaml
Copy code

---

## 📦 Install Dependencies

From the `frontend/` folder:

```bash
npm install
This installs:

Vite 5

Vitest

chess.js

▶️ Run Local Development Server
bash
Copy code
npm run dev
Vite will output a URL similar to:

arduino
Copy code
http://localhost:5173
Open it in your browser.

Hot reloading and module graph updates are automatic.

🧪 Running Tests
Frontend tests use Vitest with JSDOM.

Run all tests:

bash
Copy code
npm test
Open the interactive UI test runner:

bash
Copy code
npm run test:ui
Vitest will open a browser-like UI for viewing test results and coverage.

🏗 Build for Production
Create an optimized bundle:

bash
Copy code
npm run build
The production files will be generated in:

bash
Copy code
frontend/dist/
This folder is what gets deployed to GitHub Pages.

🚀 Deployment (GitHub Pages)
Build:

bash
Copy code
npm run build
Push the contents of dist/ to the gh-pages branch:

bash
Copy code
git subtree push --prefix frontend/dist origin gh-pages
In GitHub:

Go to Settings → Pages

Set the publishing source to gh-pages

Add custom domain: chess.johnboen.com

Add DNS record:

lua
Copy code
CNAME chess.johnboen.com → bonjohen.github.io
📁 Project Structure
css
Copy code
frontend/
  index.html
  package.json
  vite.config.js
  src/
    main.js
    ui/
    core/
    utils/
    api/
  tests/
📣 Notes
No framework (React/Vue/etc.) is required.

All logic is in ES modules for clarity and testability.

The backend is optional; the UI works 100% client-side for MVP.

