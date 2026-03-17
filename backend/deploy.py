"""
Production deployment script for Render.com
"""
import subprocess
import os
import sys

def run_command(cmd):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def deploy():
    """Deploy to Render."""
    print("Preparing for production deployment...")
    
    # Install dependencies
    print("Installing dependencies...")
    run_command("pip install -r requirements.txt")
    
    # Create database tables
    print("Creating database tables...")
    import sys
    sys.path.insert(0, os.path.abspath('.'))
    from app.models import create_tables
    create_tables()
    
    print("Deployment preparation complete!")
    print("\nTo deploy to Render:")
    print("1. Connect your GitHub repository")
    print("2. Set environment variables in Render dashboard")
    print("3. Deploy from main branch")

if __name__ == "__main__":
    deploy()
