import sys
import io
import os
import gc
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import seaborn as sns
import numpy as np

class PythonInterpreter:
    def __init__(self):
        self.output_dir = "./outputs"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def execute(self, code):
        output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        
        try:
            plt.switch_backend('Agg') 
            plt.clf()
            plt.close('all')
            
            exec_globals = {"plt": plt, "sns": sns, "pd": pd, "np": np, "os": os,"datetime": datetime}
            exec(code, exec_globals)
            
            fig = plt.gcf()
            has_plot = len(fig.get_axes()) > 0
            
            filename = None
            if has_plot:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analise_{timestamp}.png"
                path = os.path.join(self.output_dir, filename)
                fig.savefig(path)
                plt.close(fig) 
            
            return {
                "success": True, 
                "log": output.getvalue(), 
                "plot": path if has_plot else None, 
                "filename": filename
            }
        except Exception as e:
            return {"success": False, "log": str(e), "plot": None}
        finally:
            sys.stdout = original_stdout 
            gc.collect() 