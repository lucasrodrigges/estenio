"""Estenio — interactive media downloader. Entry point."""

import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from estenio.checks import check_dependencies, all_present
from estenio.steps import ask_source, ask_type, ask_format, ask_url
from estenio.downloader import download, detect_browser, convert_stories_url


VERSION = "0.2.0"
console = Console()


def show_banner() -> None:
    """Display the welcome banner."""
    title = Text("Estenio", style="bold cyan")
    subtitle = Text(f"v{VERSION} — YouTube + Instagram Downloader", style="dim")
    banner = Text.assemble(title, "\n", subtitle)
    console.print(Panel(banner, border_style="cyan"))


def show_missing_deps(missing: list) -> None:
    """Show install instructions for missing dependencies and exit."""
    console.print("\n[bold red]❌ Dependências faltando:[/bold red]\n")
    for dep in missing:
        console.print(f"  • [bold]{dep.name}[/bold] não encontrado(a).")
        console.print(f"    Instale com: [dim]{dep.install_cmd}[/dim]\n")
    console.print("[yellow]Depois de instalar, execute [bold]estenio[/bold] novamente.[/yellow]")
    sys.exit(1)


def main() -> None:
    """Main entry point: checks → welcome → loop( steps → download )."""
    # --- CLI flags ---
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("--version", "-v"):
            show_banner()
            sys.exit(0)
        if arg in ("--help", "-h"):
            show_banner()
            console.print("\nUso: estenio\n")
            console.print("CLI interativa para baixar vídeos e áudio do YouTube e Instagram.\n")
            console.print("Flags:")
            console.print("  --version, -v    Mostra a versão")
            console.print("  --help, -h       Mostra esta ajuda\n")
            sys.exit(0)

    # --- Pre-flight: dependency checks ---
    results = check_dependencies()
    if not all_present(results):
        missing = [r for r in results if not r.present]
        show_banner()
        show_missing_deps(missing)

    # --- Main loop ---
    show_banner()

    while True:
        try:
            # Step 1: Source
            source = ask_source()

            # Step 2: Type (depends on source)
            download_type = ask_type(source)

            # Step 3: Format (conditional — only for YouTube audio/both)
            audio_format = None
            if source == "youtube":
                audio_format = ask_format(download_type)

            # Step 4: URL
            url = ask_url(source, download_type)

            # --- Instagram: convert stories URL + detect browser ---
            browser = None
            if source == "instagram":
                if download_type == "stories":
                    url = convert_stories_url(url)
                browser = detect_browser()
                if not browser:
                    console.print(
                        "\n[bold red]❌ Nenhum navegador compatível encontrado.[/bold red]"
                    )
                    console.print(
                        "[yellow]Faça login no Instagram pelo Firefox ou Chrome "
                        "e tente novamente.[/yellow]\n"
                    )
                    continue

            # --- Download ---
            console.print(f"\n[bold yellow]⬇  Iniciando download...[/bold yellow]\n")
            error = download(source, download_type, audio_format, url, browser)

            if error:
                console.print(f"\n[bold red]❌ {error}[/bold red]")
                console.print("[dim]Tente com outro link.[/dim]\n")
            else:
                console.print(f"\n[bold green]✅ Download concluído![/bold green]")
                console.print(f"[dim]Arquivo salvo no diretório atual.[/dim]\n")

        except KeyboardInterrupt:
            console.print("\n\n[dim]Até mais! 👋[/dim]\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
