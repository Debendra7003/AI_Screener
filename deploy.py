#!/usr/bin/env python
"""
Deployment script for AI Interview Screener
Supports Heroku, Railway, and other cloud platforms
"""

import os
import sys
import subprocess
import json


def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ Success: {description}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description}")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return None


def setup_environment():
    """Setup environment variables"""
    env_vars = {
        'DEBUG': 'False',
        'ALLOWED_HOSTS': 'your-domain.com',
        'API_KEY': 'your-secure-api-key',
        'SECRET_KEY': 'your-django-secret-key',
        'TWILIO_ACCOUNT_SID': 'your-twilio-sid',
        'TWILIO_AUTH_TOKEN': 'your-twilio-token',
        'TWILIO_PHONE_NUMBER': 'your-twilio-number',
        'OPENAI_API_KEY': 'your-openai-key',
        'WHITELISTED_PHONE_NUMBERS': '+1234567890',
        'REDIS_URL': 'redis://localhost:6379/0'
    }
    
    print("Environment variables to set:")
    for key, value in env_vars.items():
        print(f"  {key}={value}")
    
    return env_vars


def deploy_heroku():
    """Deploy to Heroku"""
    print("\n=== Deploying to Heroku ===")
    
    # Check if Heroku CLI is installed
    if not run_command("heroku --version", "Checking Heroku CLI"):
        print("Please install Heroku CLI first")
        return False
    
    # Create Heroku app
    app_name = input("Enter Heroku app name (or press Enter to auto-generate): ").strip()
    if app_name:
        run_command(f"heroku create {app_name}", "Creating Heroku app")
    else:
        run_command("heroku create", "Creating Heroku app")
    
    # Add Redis addon
    run_command("heroku addons:create heroku-redis:mini", "Adding Redis addon")
    
    # Set environment variables
    env_vars = setup_environment()
    for key, value in env_vars.items():
        if key != 'REDIS_URL':  # Redis URL is set by addon
            heroku_value = input(f"Enter value for {key} (default: {value}): ").strip() or value
            run_command(f"heroku config:set {key}={heroku_value}", f"Setting {key}")
    
    # Deploy
    run_command("git add .", "Adding files to git")
    run_command('git commit -m "Deploy to Heroku"', "Committing changes")
    run_command("git push heroku main", "Deploying to Heroku")
    
    # Run migrations
    run_command("heroku run python manage.py migrate", "Running migrations")
    run_command("heroku run python manage.py collectstatic --noinput", "Collecting static files")
    
    # Get app URL
    app_url = run_command("heroku info -s | grep web_url | cut -d= -f2", "Getting app URL")
    if app_url:
        print(f"\n✓ Deployment successful!")
        print(f"App URL: {app_url.strip()}")
        print(f"Admin URL: {app_url.strip()}/admin/")
        
        # Update Postman environment
        update_postman_environment(app_url.strip())
    
    return True


def deploy_railway():
    """Deploy to Railway"""
    print("\n=== Deploying to Railway ===")
    
    print("To deploy to Railway:")
    print("1. Push your code to GitHub")
    print("2. Connect your GitHub repo to Railway")
    print("3. Set the following environment variables in Railway dashboard:")
    
    env_vars = setup_environment()
    for key, value in env_vars.items():
        print(f"   {key}={value}")
    
    print("\n4. Railway will automatically deploy on git push")
    return True


def update_postman_environment(base_url):
    """Update Postman environment with deployed URL"""
    env_file = "postman/AI_Interview_Screener.postman_environment.json"
    
    try:
        with open(env_file, 'r') as f:
            env_data = json.load(f)
        
        # Update BASE_URL
        for var in env_data['values']:
            if var['key'] == 'BASE_URL':
                var['value'] = base_url.rstrip('/')
                break
        
        with open(env_file, 'w') as f:
            json.dump(env_data, f, indent=2)
        
        print(f"✓ Updated Postman environment with URL: {base_url}")
        
    except Exception as e:
        print(f"✗ Error updating Postman environment: {e}")


def main():
    """Main deployment function"""
    print("AI Interview Screener Deployment Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("manage.py"):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Choose deployment platform
    print("\nChoose deployment platform:")
    print("1. Heroku")
    print("2. Railway")
    print("3. Manual setup instructions")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        deploy_heroku()
    elif choice == "2":
        deploy_railway()
    elif choice == "3":
        print("\n=== Manual Deployment Instructions ===")
        print("1. Set up your cloud platform (AWS, GCP, Azure, etc.)")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Set environment variables:")
        setup_environment()
        print("4. Run migrations: python manage.py migrate")
        print("5. Collect static files: python manage.py collectstatic")
        print("6. Start server: gunicorn ai_interview_screener.wsgi")
        print("7. Start Celery worker: celery -A ai_interview_screener worker")
    else:
        print("Invalid choice")
        sys.exit(1)
    
    print("\n=== Post-Deployment Steps ===")
    print("1. Update Twilio webhook URLs with your deployed domain")
    print("2. Test the Postman collection with your deployed API")
    print("3. Create a superuser: python manage.py createsuperuser")
    print("4. Verify phone number whitelist configuration")
    print("5. Test end-to-end interview flow")


if __name__ == "__main__":
    main()
