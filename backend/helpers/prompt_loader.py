import os

def load_prompt(relative_path: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))

    print("base dir: ", base_dir)
    print("root dir: ", root_dir)

    full_path = os.path.join(root_dir, relative_path)
    print("full path: ", full_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Prompt file not found at: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()
