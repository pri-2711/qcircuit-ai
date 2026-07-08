import streamlit as st

from simulator.execute import execute_user_code
from ui.editor import render_code_editor

st.set_page_config(page_title="Quantum Circuit Explorer", page_icon="⚛️", layout="centered")

DEFAULT_CODE = """from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
"""


def main() -> None:
    st.title("Quantum Circuit Explorer & AI Tutor")
    st.caption("Write Qiskit code, run it, and inspect the generated circuit.")

    code = render_code_editor(initial_code=DEFAULT_CODE)
    run_clicked = st.button("Run", type="primary")

    if run_clicked:
        result = execute_user_code(code)

        if result["success"]:
            st.success("Circuit executed successfully.")
            st.write("Generated circuit:")
            st.code(str(result["circuit"]), language="text")
            st.caption(
                f"Qubits: {result['circuit'].num_qubits}, Classical bits: {result['circuit'].num_clbits}"
            )
        else:
            st.error("Execution failed.")
            st.code(result["error"], language="text")


if __name__ == "__main__":
    main()
