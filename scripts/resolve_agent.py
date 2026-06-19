import subprocess
import sys

def run_command(cmd, name):
    print(f"Running {name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"{name} completed successfully.")
    else:
        print(f"{name} completed with warning/error (exit code {result.returncode}):")
        print(result.stdout)
        print(result.stderr)

def main():
    print("=== Auto-Resolution Agent ===")
    
    # 1. Autoflake to remove unused imports and variables
    run_command(
        ["uv", "run", "--with", "autoflake", "autoflake", "--remove-all-unused-imports", "--in-place", "--recursive", "src"],
        "autoflake"
    )
    
    # 2. Isort to sort imports
    run_command(
        ["uv", "run", "--with", "isort", "isort", "src"],
        "isort"
    )
    
    # 3. Black to format code
    run_command(
        ["uv", "run", "--with", "black", "black", "src"],
        "black"
    )
    
    print("Auto-resolution formatting complete.")

if __name__ == "__main__":
    main()
