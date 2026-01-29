from rich.console import Console

console = Console()

# shared global status for pausing/resuming
global_status =  console.status("[bold dark_orange]🐱 psspssss...", spinner="dots", spinner_style="dark_orange")