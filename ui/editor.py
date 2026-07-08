import streamlit as st


def render_code_editor(initial_code: str = "", key: str = "user_code") -> str:
    st.subheader("Qiskit editor")
    return st.text_area(
        "Write your Qiskit code",
        value=initial_code,
        height=280,
        key=key,
        placeholder="from qiskit import QuantumCircuit\n\nqc = QuantumCircuit(2)\nqc.h(0)\n",
    )
