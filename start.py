#!/usr/bin/env python3
"""
Globe News Frontend Startup Script
This script starts the Flask frontend server.
"""

import os
import sys
import subprocess
import time
import webbrowser
import requests
from pathlib import Path

def print_banner():
    """Print startup banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                    GLOBE NEWS FRONTEND                   ║
    ║                   🚀 Starting Server...                   ║
    ╚══════════════════════════════════════════════════════════╝
    
    🌐 Modern Web Interface for Global News
    🎨 Beautiful, Responsive Design
    🔗 Connected to Backend API
    """
    print(banner)

def check_backend():
    """Check if backend server is running."""
    print("🔗 Checking backend connection...")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/health/status", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            
            # Get backend info
            try:
                info_response = requests.get("http://localhost:8000/", timeout=5)
                if info_response.status_code == 200:
                    info = info_response.json()
                    print(f"   📊 Version: {info.get('version', 'Unknown')}")
                    print(f"   📰 Articles: {info.get('statistics', {}).get('total_articles', 0)}")
            except:
                pass
            
            return True
        else:
            print(f"⚠️  Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        print("   Please start the backend server first:")
        print("   cd ../backend && python start.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'flask',
        'requests'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing modules: {', '.join(missing_modules)}")
        print("📦 Installing missing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please install them manually:")
            print(f"   pip install {' '.join(missing_modules)}")
            return False
    
    print("✅ All dependencies are available")
    return True

def check_templates():
    """Check if required template files exist."""
    print("📄 Checking template files...")
    
    required_templates = [
        'index.html',
        'article_detail.html',
        'category.html',
        'category_detail.html',
        'breaking.html',
        'search.html',
        'stats.html',
        'error.html'
    ]
    
    templates_dir = 'templates'
    missing_templates = []
    
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if not os.path.exists(template_path):
            missing_templates.append(template)
    
    if missing_templates:
        print(f"⚠️  Missing templates: {', '.join(missing_templates)}")
        print("   Some pages may not work properly.")
    else:
        print("✅ All template files found")
    
    return True

def start_server(host='0.0.0.0', port=5000, debug=True):
    """Start the Flask server."""
    print(f"🚀 Starting frontend server on http://{host}:{port}")
    print("─" * 60)
    
    # Build Flask command
    cmd = [
        sys.executable,
        "app.py"
    ]
    
    # Set environment variables
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development' if debug else 'production'
    env['FLASK_DEBUG'] = '1' if debug else '0'
    
    try:
        # Start the server
        process = subprocess.Popen(cmd, env=env)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        print("✅ Frontend server started successfully!")
        print("\n📋 Available Pages:")
        print("   /                   - Home page")
        print("   /categories         - All categories")
        print("   /category/<name>    - Category details")
        print("   /breaking           - Breaking news")
        print("   /article/<id>       - Article details")
        print("   /search             - Search news")
        print("   /stats              - Statistics")
        print("\n🎮 Press Ctrl+C to stop the server")
        
        # Open browser if requested
        if input("\n🌐 Open frontend in browser? (y/n): ").lower() == 'y':
            webbrowser.open(f"http://{host}:{port}")
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def run_frontend_tests():
    """Run basic frontend tests."""
    print("\n🧪 Running frontend tests...")
    
    import requests
    import time
    
    # Wait a bit for server to be ready
    time.sleep(3)
    
    test_pages = [
        ("/", "Home page"),
        ("/categories", "Categories page"),
        ("/breaking", "Breaking news"),
    ]
    
    all_passed = True
    
    for page, description in test_pages:
        try:
            response = requests.get(f"http://localhost:5000{page}", timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {description}: HTTP {response.status_code}")
            else:
                print(f"  ❌ {description}: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  ❌ {description}: Failed - {e}")
            all_passed = False
    
    if all_passed:
        print("✅ All frontend tests passed!")
    else:
        print("⚠️  Some frontend tests failed.")
    
    return all_passed

def show_help():
    """Show help information."""
    help_text = """
    Globe News Frontend Startup Script
    Usage: python start.py [options]
    
    Options:
      --help, -h           Show this help message
      --host HOST          Set host address (default: 0.0.0.0)
      --port PORT          Set port number (default: 5000)
      --no-debug           Disable debug mode (production)
      --test               Run tests after starting
      --no-browser         Don't open browser automatically
      --skip-backend-check Skip backend connection check
    
    Examples:
      python start.py                     # Start with default settings
      python start.py --port 5050         # Start on port 5050
      python start.py --no-debug          # Start without debug mode
      python start.py --test              # Run tests after startup
    """
    print(help_text)

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Globe News Frontend Startup Script", add_help=False)
    parser.add_argument('--help', '-h', action='store_true', help='Show help message')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=5000, help='Port number')
    parser.add_argument('--no-debug', action='store_true', help='Disable debug mode')
    parser.add_argument('--test', action='store_true', help='Run tests after starting')
    parser.add_argument('--no-browser', action='store_true', help="Don't open browser")
    parser.add_argument('--skip-backend-check', action='store_true', help='Skip backend connection check')
    
    args = parser.parse_args()
    
    if args.help:
        show_help()
        return
    
    # Print banner
    print_banner()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check templates
    check_templates()
    
    # Check backend (unless skipped)
    if not args.skip_backend_check and not check_backend():
        print("\n⚠️  Starting without backend connection...")
        print("   Some features may not work properly.")
    
    # Start server
    success = start_server(
        host=args.host,
        port=args.port,
        debug=not args.no_debug
    )
    
    if success and args.test:
        run_frontend_tests()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)