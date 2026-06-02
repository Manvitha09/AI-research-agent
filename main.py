import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from agent import run_agent
from report import save_report

console = Console()


def main():
    console.print(Panel.fit(
        "[bold blue]🤖 AI Research Agent[/bold blue]\n"
        "[dim]Powered by Gemini + Tavily[/dim]",
        border_style="blue"
    ))

    # Get topic from CLI arg or prompt user
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = console.input("\n[bold]Enter a research topic:[/bold] ").strip()

    if not topic:
        console.print("[red]No topic provided. Exiting.[/red]")
        sys.exit(1)

    console.print(f"\n[bold green]Starting research on:[/bold green] {topic}\n")

    try:
        report = run_agent(topic)

        # Display in terminal
        console.print("\n" + "="*60)
        console.print(Markdown(report))

        # Save to file
        filename = save_report(topic, report)
        console.print(f"\n[bold green]✅ Report saved to:[/bold green] {filename}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()