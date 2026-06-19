import subprocess
import sys

def main():
    print("=== Lint Verification Agent ===")
    cmd = ["uv", "run", "--with", "flake8", "flake8", "src"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Lint check passed! No errors found.")
        sys.exit(0)
    else:
        print("Lint check failed with the following errors:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
