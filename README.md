# Quantum Circuit Explorer & AI Tutor

## Aim

A web-based platform that enables users to write, import, and analyze quantum circuits in multiple formats (Qiskit, OpenQASM, and eventually Cirq). The platform acts as an intelligent quantum tutor by visualizing circuits, simulating their behavior, providing mathematical and theoretical explanations, identifying similarities with known quantum algorithms, and suggesting optimizations.

## Key Features

* Multi-language quantum circuit support (Qiskit, OpenQASM, Cirq).
* Interactive code editor and circuit visualization.
* Quantum simulation with statevector and measurement probability analysis.
* AI-powered explanations of gate operations, circuit behavior, and underlying mathematics.
* Detection of known algorithms and patterns (Bell states, Grover's algorithm, QFT, VQE ansätze, etc.).
* Circuit statistics and analysis (depth, gate counts, qubits, entanglement).
* Conversational AI assistant for answering questions, debugging, and explaining concepts.
* Circuit optimization suggestions and simplifications.
* Extensible architecture for future research on circuit similarity search and automated circuit design.

## Proposed Tech Stack

* **Frontend:** React, Vite, Monaco Editor, Tailwind CSS
* **Backend:** Python, FastAPI
* **Quantum Frameworks:** Qiskit, OpenQASM Parser, Cirq (future support), PennyLane (future integration)
* **AI Layer:** LLM APIs (Gemini/OpenAI), LangChain/LangGraph
* **Data & Storage:** JSON-based knowledge base and algorithm database

## Implementation Flow

1. User writes or uploads a quantum circuit.
2. Backend parses the circuit into a unified intermediate representation.
3. Quantum simulator executes the circuit and generates:

   * Circuit diagram
   * Statevector
   * Measurement probabilities
   * Circuit statistics
4. Analyzer detects entanglement, identifies algorithmic patterns, and searches for similarities with known circuits.
5. AI agent generates mathematical explanations, theoretical insights, and optimization recommendations.
6. Results are displayed through an interactive web interface with conversational support.

## Expected Outcome

A beginner-friendly yet research-oriented platform that bridges quantum computing and AI, making quantum circuits easier to understand, analyze, and design while serving as an educational tool and foundation for future work in automated quantum circuit synthesis.
