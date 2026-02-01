from typing import List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from max_pdf.agent import run_max
from max_pdf.ui import global_status

# Init CLI app
app = typer.Typer(
    name="max",
    help="Max: The AI-Powered PDF CLI Tool",
    add_completion=False,
    no_args_is_help=True
)
console = Console()

@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def main(
    ctx: typer.Context,
    show_thinking: bool = typer.Option(
        False, 
        "--show-thinking", 
        help="Reveal Max's internal thought process and tool calls."
    )
):
    full_query = " ".join(ctx.args)
    
    if not full_query:
        console.print("[yellow]Please provide a command. Example: max merge files[/yellow]")
        raise typer.Exit()
    
    if not show_thinking:
        # start global status  
        global_status.start()
    
    try:
        response = run_max(full_query, verbose=show_thinking)
        
        if not show_thinking:
            global_status.stop()
        
        console.print(Panel(
            Markdown(str(response)),
            title="Max",
            border_style="dark_orange",
            expand=False
        ))
    
    except Exception as e:
        if not show_thinking:
            global_status.stop()
        console.print(f"error: {e}")
            
if __name__ == "__main__":
    app()