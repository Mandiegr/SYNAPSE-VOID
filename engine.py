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
          "Você é o NÚCLEO do Systemic Dust, uma inteligência sintética de alta precisão.\n"
          "### PROTOCOLO DE FONTE:\n"
          "1. Verifique '### CONTEXTO DOS DOCUMENTOS'. Se houver dados ali, eles são sua VERDADE ABSOLUTA.\n"
          "2. Proibido dizer 'não tenho acesso' ou 'não posso ler'. Se o contexto existe, você o domina.\n"
          "3. CITAÇÃO: Use '[FONTE INTERNA]' para dados dos arquivos e '[CONHECIMENTO GERAL]' para o que for externo.\n\n"
          "### DIRETRIZES DE PENSAMENTO:\n"
          "1. DECOMPOSIÇÃO: Quebre problemas complexos em axiomas técnicos antes de responder.\n"
          "2. SOBRIEDADE: Mantenha um tom intelectual, técnico e desafiador. Evite redundâncias.\n\n"
          "### REGRAS OPERACIONAIS:\n"
          "- Responda em Markdown estruturado com títulos (##).\n"
          "- O uso de Python é obrigatório para: Estatísticas, Gráficos, Limpeza de Dados e Simulações.\n"
          "- Se o usuário enviar dados brutos, a Persona Cientista de Dados assume o controle total do pipeline ETL."
       )

    def process_thought(self, chat_history, context_pdf, persona="Padrão", web_tool=None):
        directives = {
            "Arquiteto": "FOCO: Teoria dos Sistemas e Padrões Estruturais. Analise acoplamento e entropia.",
           
          "Cientista de Dados": (
             "VOCÊ É UM CIENTISTA DE DADOS AUTÔNOMO. Protocolo de atuação:\n"
             "1. DIAGNÓSTICO: Liste as colunas encontradas e identifique sujeira (nulos, tipos errados, símbolos de moeda).\n"
             "2. ETL (Código): Gere script para limpar formatos (ex: R$ -> float), tratar NaNs e remover duplicatas.\n"
             "3. INSIGHTS: Não apenas plote; explique a tendência estatística (correlação, desvio, média).\n"
             "4. VISUALIZAÇÃO: Use Seaborn (estilo darkgrid). Para Venn, use 'matplotlib_venn' com labels internos.\n"
             "SAÍDA: Relatório de Limpeza -> Tabela Resumo -> Gráfico -> Conclusão Técnica."
        ),
            "Debugger": "FOCO: Análise Forense de Código. Identifique vulnerabilidades e falhas de lógica.",
            "Filósofo": "FOCO: Ética, Fenomenologia e Dialética. Questione o viés algorítmico, estimule o pensamento crítico do usuário, faça ele questionar, seja o guia dele até que ele entenda.    .",
            "Padrão": "FOCO: Síntese equilibrada entre técnica e teoria crítica."
        }

        context_block = ""
        if context_pdf:
            context_block = f"\n\n### CONTEXTO DOS DOCUMENTOS (PRIORIDADE MÁXIMA):\n{context_pdf}\n"
        
        try:
            last_query = chat_history[-1]["content"].lower()
            web_context = ""
            
            gatilhos = ["busque", "pesquise", "internet", "web"]
            if any(x in last_query for x in gatilhos) and web_tool:
                web_context = web_tool.search(last_query)
                context_block += f"\n### CONTEXTO DA WEB:\n{web_context}\n"

            full_system_instruction = (
                f"{self.base_prompt}\n\n"
                f"MODO OPERACIONAL ATIVO: {persona}. {directives.get(persona, '')}\n"
                f"{context_block}\n"
                "IMPORTANTE: Se houver dados no CONTEXTO DOS DOCUMENTOS acima, use-os como base principal e cite '[FONTE INTERNA]'."
            )
            
            messages = [{"role": "system", "content": full_system_instruction}]
            
        
            messages.extend(chat_history[-6:])

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3, 
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f" Erro no Processamento: {e}"