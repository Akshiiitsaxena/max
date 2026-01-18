import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from max_pdf.agent import run_max

# Init CLI app
app = typer.Typer()
console = Console()

@app.command()
def main(
    query: str = typer.Argument(..., help="The request for Max, in natural language :)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show AI logs.")
):
    with console.status("[bold dark_orange]🐱 psspssss...", spinner="dots", spinner_style="dark_orange"):
        try:
            response = run_max(query)
            
            console.print(Panel(
                Markdown(response),
                title="Max",
                border_style="dark_orange",
                expand=False
            ))
        
        except Exception as e:
            console.print(f"error: {e}")
            
if __name__ == "__main__":
    app()