from fpdf import FPDF
import datetime
import os


class ReportGenerator:
    def __init__(self):
        self.output_dir = "./reports"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_pdf(self, history):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        pdf.set_font("Courier", "B", 16)
        pdf.cell(200, 10, txt="SYSTEMIC DUST - RELATÓRIO OPERACIONAL", ln=True, align='C')
        pdf.set_font("Courier", "I", 10)
        pdf.cell(200, 10, txt=f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
        pdf.ln(10)

        for entry in history:

            if entry["role"] == "user":
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("Courier", "B", 12)
                pdf.multi_cell(0, 10, txt=f"COMANDO: {entry['content']}", border=1, fill=True)
                pdf.ln(5)
            
            elif entry["role"] == "assistant":
                pdf.set_font("Courier", "", 11)
               
                clean_text = entry['content'].encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 8, txt=clean_text)
                pdf.ln(5)

    
        if os.path.exists("./outputs"):
            output_files = sorted([f for f in os.listdir("./outputs") if f.endswith(".png")])
            if output_files:
                last_plot = os.path.join("./outputs", output_files[-1])
                pdf.add_page()
                pdf.set_font("Courier", "B", 12)
                pdf.cell(0, 10, txt="ANÁLISE GRÁFICA ANEXADA:", ln=True)
                pdf.image(last_plot, x=10, y=30, w=180)

        report_name = f"relatorio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        report_path = os.path.join(self.output_dir, report_name)
        pdf.output(report_path)
        return report_path, report_name