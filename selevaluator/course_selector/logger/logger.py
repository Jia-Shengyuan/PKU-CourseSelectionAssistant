from rich.console import Console

class Logger:

    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.console = Console()
        return cls._instance

    def log(self, message : str, *args, **kwargs) -> None:
        self.console.print(message, *args, **kwargs)

    def log_error(self, message : str, *args, **kwargs) -> None:
        self.console.print(f"[bold red]ERROR : [/bold red]{message}", *args, **kwargs)

    def log_warning(self, message : str, *args, **kwargs) -> None:
        self.console.print(f"[bold yellow]WARNING : [/bold yellow]{message}", *args, **kwargs)

    def log_info(self, message : str, *args, **kwargs) -> None:
        self.console.print(f"[bold green]INFO : [/bold green]{message}", *args, **kwargs)
        

