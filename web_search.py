from tavily import TavilyClient
import os

class WebSearchTool:
    def __init__(self):
       
        self.api_key = os.getenv("TAVILY_API_KEY")
        try:
            if self.api_key:
                self.client = TavilyClient(api_key=self.api_key)
            else:
                self.client = None
        except Exception:
            self.client = None

    def search(self, query):
    
        if not self.client:
            return " (Nota: Busca Web indisponível no momento - Chave API não configurada)."
        
        try:
            response = self.client.search(
                query, 
                search_depth="advanced", 
                max_results=10,
                include_answer=True 
            )
            
            context = "\n\n--- INFORMAÇÕES ADICIONAIS DA WEB ---\n\n"
            if 'answer' in response and response['answer']:
                context += f"RESUMO DA BUSCA: {response['answer']}\n\n"
            
            for result in response['results']:
                context += f"Fonte: {result['url']}\n"
                context += f"Conteúdo Relevante: {result['content']}\n\n"
                
            return context
        except Exception as e:
            return f"\n (Erro ao acessar a Web: {e})\n"