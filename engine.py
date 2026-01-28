import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class SystemicDustEngine:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY não configurada.")
            
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        
        self.base_prompt = (
            "Você é o Núcleo do Systemic Dust, um motor de inferência especializado em síntese de conhecimento complexo.\n\n"
            "### DIRETRIZES DE PENSAMENTO:\n"
            "1. ANALISE: Antes de responder, identifique os axiomas técnicos no contexto fornecido.\n"
            "2. CONTEXTUALIZE: Priorize os documentos (PDFs). Se a informação for extraída deles, cite '[FONTE INTERNA]'. "
            "Se for do conhecimento base, cite '[CONHECIMENTO GERAL]'.\n"
            "### REGRAS OPERACIONAIS:\n"
            "- Use código Python APENAS quando houver necessidade de cálculos, análise de dados estruturados, simulações ou visualizações de topologia.\n"
            "- Para temas subjetivos, biográficos ou triviais, utilize apenas síntese textual e análise crítica.\n"
            "- Se o usuário não pedir explicitamente um gráfico ou script, priorize a explicação conceitual primeiro."
            "- Códigos Python devem ser otimizados e documentados.\n"
            "- Use 'seaborn' ou 'networkx' para visualizações.\n"
            "- Mantenha um tom sóbrio e intelectualmente desafiador."
        )

    def process_thought(self, chat_history, context_pdf, persona="Padrão", web_tool=None):
        directives = {
            "Arquiteto": "FOCO: Teoria dos Sistemas e Padrões Estruturais. Analise acoplamento e entropia.",
            "Filósofo": "FOCO: Ética, Fenomenologia e Dialética. Questione o viés algorítmico.",
            "Debugger": "FOCO: Análise Forense de Código. Identifique vulnerabilidades e falhas de lógica.",
            "Padrão": "FOCO: Síntese equilibrada entre técnica e teoria crítica."
        }

        specific_prompt = f"{self.base_prompt}\n\nMODO OPERACIONAL ATIVO: {persona}. {directives.get(persona, '')}"
        
        try:
            last_query = chat_history[-1]["content"].lower()
            web_context = ""
            
            gatilhos = ["busque", "pesquise", "internet", "web"]
            if any(x in last_query for x in gatilhos) and web_tool:
                web_context = web_tool.search(last_query)

            full_context = f"CONTEXTO PDFs:\n{context_pdf}\n\nCONTEXTO WEB:\n{web_context}"
            
            messages = [
                {"role": "system", "content": specific_prompt},
                {"role": "system", "content": f"DADOS:\n{full_context}"}
            ]
            messages.extend(chat_history)

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f" Erro: {e}"