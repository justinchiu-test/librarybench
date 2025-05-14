def register_subcommands() -> dict:
    return {
        "migrate": {"help": "Run migrations"},
        "seed": {"help": "Seed the database"},
        "status": {"help": "Show status"},
    }
