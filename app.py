import streamlit as st
import os
import re
from engine import SystemicDustEngine
from vector_store import MemoryBank
from code_interpreter import PythonInterpreter
from web_search import WebSearchTool
from report_generator import ReportGenerator

st.set_page_config(page_title="SYNAPSE VOID", layout="wide", page_icon="🌑")


if "engine" not in st.session_state:
    st.session_state.engine = SystemicDustEngine()
    st.session_state.memory = MemoryBank()
    st.session_state.interpreter = PythonInterpreter()
    st.session_state.web_search = WebSearchTool()
    st.session_state.report_gen = ReportGenerator()
    st.session_state.chat_history = []

with st.sidebar:
    st.title(" Synapse Void")
    st.caption("v1.0.2 | Ghost in the Machine")
    st.write("---")
    
    st.divider()
    st.subheader(" Persona do Núcleo")
    persona = st.selectbox(
        "Modo de análise:",
        ["Padrão", "Arquiteto", "Filósofo", "Debugger"]
    )

    st.divider()
    files_count = len(os.listdir("./knowledge")) if os.path.exists("./knowledge") else 0
    st.metric("Documentos na Memória", f"{files_count} PDFs")
    
    st.divider()
    uploaded_files = st.file_uploader("Injetar novos PDFs", accept_multiple_files=True)
    if st.button(" Sincronizar Documentos", use_container_width=True):
        if uploaded_files:
            if not os.path.exists("./knowledge"): os.makedirs("./knowledge")
            for f in uploaded_files:
                with open(os.path.join("./knowledge", f.name), "wb") as out:
                    out.write(f.getbuffer())
            with st.spinner("Indexando..."):
                st.session_state.memory.ingest_knowledge()
                st.success("Conhecimento integrado!")
                st.rerun()
                
    st.divider()
    st.subheader("Exportar")
    if st.button("Gerar Relatório PDF", use_container_width=True):
        if st.session_state.chat_history:
            path, name = st.session_state.report_gen.create_pdf(st.session_state.chat_history)
            with open(path, "rb") as f:
                st.download_button("Baixar Arquivo", f, file_name=name, mime="application/pdf", use_container_width=True)
        else:
            st.warning("Histórico vazio.")

    if st.button("Limpar Memória", type="primary", use_container_width=True):
        st.session_state.memory.clear_memory()
        st.session_state.chat_history = []
        st.rerun()

for i, msg in enumerate(st.session_state.chat_history):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg["role"] == "assistant":
            code_blocks = re.findall(r"```python\n(.*?)\n```", msg["content"], re.DOTALL)
            if code_blocks:
                with st.expander(" Console de Execução", expanded=True):
                    st.code(code_blocks[0], language='python')
                    if st.button(" Rodar Script", key=f"run_{i}"):
                        res = st.session_state.interpreter.execute(code_blocks[0])
                        if res["success"]:
                            if res["log"]: 
                                st.info(f"Saída: {res['log']}")
                           
                            if res["plot"]: 
                                st.image(res["plot"], caption="Análise Visual - Synapse Void")
                        else:
                            st.error(res["log"])

if prompt := st.chat_input("Digite sua pergunta ou comando..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    context_pdf = st.session_state.memory.get_context(prompt)
    
    with st.spinner(f"Respondendo como {persona}..."):
        response = st.session_state.engine.process_thought(
        st.session_state.chat_history, 
        context_pdf, 
        persona=persona,  
        web_tool=st.session_state.web_search
)
        
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()