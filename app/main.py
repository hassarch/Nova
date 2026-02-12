import typer

app = typer.Typer()

@app.command()
def run(prompt: str):
    print(f"NOVA received: {prompt}")

def main():
    app()

if __name__ == "__main__":
    main()
