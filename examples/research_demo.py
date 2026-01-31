#!/usr/bin/env python3
"""
Research Capabilities Demo

This script demonstrates the research capabilities of the WormGPT Hive Mind:
- Web search using DuckDuckGo
- Content fetching from URLs
- Combined search and summarize
"""

from wormgpt_hive.tools.google_search import GoogleSearchTool
from wormgpt_hive.tools.web_browser import WebBrowserTool
from wormgpt_hive.drones.research_drone import ResearchDrone
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint


def demo_web_search():
    console = Console()
    console.print("\n[bold cyan]Demo 1: Web Search[/bold cyan]")
    
    search_tool = GoogleSearchTool(rate_limit_delay=1.0)
    
    query = "artificial intelligence breakthroughs 2024"
    console.print(f"Searching for: [yellow]{query}[/yellow]")
    
    result = search_tool.search(query, max_results=3)
    
    if result["success"]:
        console.print(f"[green]SUCCESS[/green] Found {result['data']['count']} results\n")
        
        for idx, item in enumerate(result["data"]["results"], 1):
            console.print(f"[bold]{idx}. {item['title']}[/bold]")
            console.print(f"   [dim]{item['link']}[/dim]")
            console.print(f"   {item['snippet'][:100]}...\n")
    else:
        console.print(f"[red]FAILED[/red] Search failed: {result['error']}")


def demo_web_fetch():
    console = Console()
    console.print("\n[bold cyan]Demo 2: Web Content Fetching[/bold cyan]")
    
    browser_tool = WebBrowserTool(rate_limit_delay=1.0)
    
    url = "https://example.com"
    console.print(f"Fetching: [yellow]{url}[/yellow]")
    
    result = browser_tool.fetch(url, parse_content=True)
    
    if result["success"]:
        console.print(f"[green]SUCCESS[/green] Fetched {result['data']['content_length']} characters\n")
        console.print(f"[bold]Title:[/bold] {result['data']['title']}")
        console.print(f"[bold]Text Preview:[/bold]")
        console.print(Panel(result['data']['text'][:500], border_style="dim"))
    else:
        console.print(f"[red]FAILED[/red] Fetch failed: {result['error']}")


def demo_research_drone():
    console = Console()
    console.print("\n[bold cyan]Demo 3: Research Drone - Search and Summarize[/bold cyan]")
    
    search_tool = GoogleSearchTool(rate_limit_delay=2.0)
    browser_tool = WebBrowserTool(rate_limit_delay=2.0)
    
    research_drone = ResearchDrone()
    research_drone.register_tool("google_search", search_tool)
    research_drone.register_tool("web_browser", browser_tool)
    
    query = "Python programming tutorials"
    console.print(f"Researching: [yellow]{query}[/yellow]")
    
    result = research_drone.execute(
        "search_and_summarize",
        {
            "query": query,
            "max_results": 3,
            "fetch_top_n": 1
        }
    )
    
    if result["success"]:
        data = result["data"]
        console.print(f"[green]SUCCESS[/green] Found {data['total_results']} results, fetched {data['fetched_count']} articles\n")
        
        console.print("[bold]Search Results:[/bold]")
        for item in data["search_results"]:
            console.print(f"  - {item['title']}")
            console.print(f"    [dim]{item['link']}[/dim]")
        
        if data["fetched_content"]:
            console.print(f"\n[bold]Fetched Article:[/bold]")
            article = data["fetched_content"][0]
            console.print(f"[bold]{article['title']}[/bold]")
            console.print(f"[dim]{article['url']}[/dim]")
            console.print(f"\n{article['full_text'][:500]}...")
    else:
        console.print(f"[red]FAILED[/red] Research failed: {result['error']}")


if __name__ == "__main__":
    console = Console()
    
    console.print(Panel.fit(
        "[bold green]WormGPT Hive Mind - Research Capabilities Demo[/bold green]",
        border_style="green"
    ))
    
    try:
        demo_web_search()
        demo_web_fetch()
        demo_research_drone()
        
        console.print("\n[bold green]All demos completed successfully![/bold green]\n")
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
