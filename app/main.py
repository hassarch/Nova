import typer
from rich import print
from app.database.connection import SessionLocal
from app.agent.controller import AgentController

app = typer.Typer()


@app.command()
def run(prompt: str):

    db = SessionLocal()
    controller = AgentController(db)

    plan = controller.run(prompt)

    print("[bold green]Generated Plan:[/bold green]")
    print(plan)


def main():
    app()


if __name__ == "__main__":
    main()
