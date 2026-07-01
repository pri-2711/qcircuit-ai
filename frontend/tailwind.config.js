/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        void: "#0B0E14",
        slate: "#141821",
        slateline: "#232A38",
        mist: "#E4E7EC",
        fog: "#8A93A6",
        phase0: "#4FD8EB",   // phase 0deg   - coherent / primary actions
        phase90: "#B98EFF",  // phase 90deg  - entanglement / correlation
        phase180: "#FF7B72", // phase 180deg - errors / decoherence
        phase270: "#FFC46B", // phase 270deg - optimization / energy
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
        sans: ["'Inter'", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
