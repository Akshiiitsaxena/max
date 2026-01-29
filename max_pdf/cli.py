from typing import List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from max_pdf.agent import run_max
from max_pdf.ui import global_status

# Init CLI app
app = typer.Typer()
console = Console()

@app.command()
def main(
    query_parts: List[str] = typer.Argument(..., help="The request for Max, in natural language :)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show AI logs.")
):
    full_query = " ".join(query_parts)
    
    # start global status  
    global_status.start()
    try:
        response = run_max(full_query)
        global_status.stop()
        
        console.print(Panel(
            Markdown(str(response)),
            title="Max",
            border_style="dark_orange",
            expand=False
        ))
    
    except Exception as e:
        console.print(f"error: {e}")
            
if __name__ == "__main__":
    app()