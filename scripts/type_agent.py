import subprocess
import sys

def main():
    print("=== Type Verification Agent ===")
    cmd = ["uv", "run", "--with", "mypy", "--with", "pydantic", "mypy", "src", "--explicit-package-bases"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Type check passed! No errors found.")
        sys.exit(0)
    else:
        print("Type check failed with the following errors:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
