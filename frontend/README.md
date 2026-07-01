# Frontend -- Quantum Circuit Explorer UI

React + Vite + Tailwind + Monaco Editor workbench for the API in `../backend`.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dev server proxies `/api/*` to
`http://localhost:8000` (see `vite.config.js`) -- **the backend must be running**
for anything to work; you'll see a banner at the top of the page if it can't be
reached.

## Layout

- **`src/components/Sidebar.jsx`** -- language tabs (Qiskit / QASM2 / QASM3) and
  the built-in example circuit library (pulled from `GET /api/examples`).
- **`src/components/CodeEditor.jsx`** -- Monaco editor + "Run simulation" button.
- **`src/components/ResultsTabs.jsx`** -- circuit diagram / statevector /
  probabilities, tabbed. Statevector amplitudes are colored by phase angle using
  a 4-anchor hue convention (cyan 0°, violet 90°, coral 180°, amber 270°) --
  the same convention used for the entanglement bars and optimization hints in
  the analysis panel, so color carries consistent meaning across the whole app.
- **`src/components/AnalysisPanel.jsx`** -- stats, per-qubit entanglement,
  detected algorithm patterns, optimization hints, "Explain this circuit" button.
- **`src/components/ChatPanel.jsx`** -- free-form conversational tutor.

## Design tokens

Defined in `tailwind.config.js`: background/surface neutrals (`void`, `slate`,
`slateline`), text (`mist`, `fog`), and the four phase-color accents
(`phase0`/`phase90`/`phase180`/`phase270`). Typography: `Fraunces` (display),
`Inter` (UI text), `JetBrains Mono` (code/data), loaded via Google Fonts in
`index.html`.

## Extending

- **Cirq**: add a third language tab in `Sidebar.jsx`'s `LANGUAGES` array; the
  backend will need a matching `"cirq"` case (see backend README's "Extending"
  section).
- **Bloch sphere / 3D visualizations**: `ResultsTabs.jsx` is the natural place
  for a fourth tab; `three` is available if you want a real 3D Bloch sphere per
  qubit instead of the amplitude bars.
- **Auth / multi-user**: none of this exists yet -- this scaffold assumes a
  single trusted local user, matching the backend's dev-grade sandbox.
