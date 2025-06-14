import os
import sys
import importlib.util
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_file_exists(filepath):
    exists = os.path.exists(filepath)
    logger.info(f"Checking {filepath}: {'✓' if exists else '✗'}")
    return exists

def check_import(module_name):
    try:
        importlib.import_module(module_name)
        logger.info(f"Importing {module_name}: ✓")
        return True
    except ImportError as e:
        logger.error(f"Importing {module_name}: ✗ ({str(e)})")
        return False

def main():
    logger.info("Starting application tests...")
    
    # Check required files
    required_files = [
        'main_app.py',
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'templates/index.html',
        'templates/admin.html',
        'templates/investor_view.html'
    ]
    
    files_ok = all(check_file_exists(f) for f in required_files)
    
    # Check required Python packages
    required_packages = [
        'flask',
        'gunicorn',
        'werkzeug',
        'jinja2'
    ]
    
    packages_ok = all(check_import(pkg) for pkg in required_packages)
    
    # Check template directory structure
    templates_dir = 'templates'
    if os.path.exists(templates_dir):
        logger.info(f"Templates directory exists: ✓")
        template_files = os.listdir(templates_dir)
        logger.info(f"Template files found: {', '.join(template_files)}")
    else:
        logger.error("Templates directory missing: ✗")
    
    # Summary
    logger.info("\nTest Summary:")
    logger.info(f"Required files: {'✓' if files_ok else '✗'}")
    logger.info(f"Required packages: {'✓' if packages_ok else '✗'}")
    
    return files_ok and packages_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 