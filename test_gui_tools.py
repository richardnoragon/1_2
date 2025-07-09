import subprocess
import sys
import time
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gui_test_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_tool(script_name, timeout=5):
    """Run a tool and monitor its execution."""
    try:
        logging.info(f"Testing {script_name}...")
        
        # Start the process
        process = subprocess.Popen(["python", script_name])
        
        # Wait for the specified timeout
        time.sleep(timeout)
        
        # Check if process is still running
        if process.poll() is None:
            logging.info(f"{script_name} opened successfully")
            process.terminate()  # Clean up
            time.sleep(1)  # Give it time to close
            if process.poll() is None:
                process.kill()  # Force kill if still running
        else:
            return_code = process.returncode
            if return_code == 0:
                logging.info(f"{script_name} executed and closed normally")
            else:
                logging.error(f"{script_name} failed with return code {return_code}")
        
    except Exception as e:
        logging.error(f"Error running {script_name}: {str(e)}")
        return False
    
    return True

def main():
    logging.info("Starting GUI tools test run")
    logging.info("=" * 50)
    
    # Dictionary of tools to test with their Python files
    tools = {
        "File Management": [
            ("File Finder", "file_finder.py"),
            ("Catalog Files", "catalog.py"),
            ("Rename Files", "rename.py")
        ],
        "Organization": [
            ("Organize Files", "organize.py"),
            ("Copy/Move/Sync/Delete", "cmsd.py"),
            ("Synchronize", "sync.py"),
            ("Find Empty Folders", "empty_folders.py")
        ],
        "Analysis": [
            ("Analyze Size", "size_analyzer.py"),
            ("Duplicate Finder", "find_duplicate_files.py"),
            ("Disk Space Analyzer", "tree_map.py"),
            ("File Checksum", "check_sum.py")
        ],
        "Operations": [
            ("Encrypt/Decrypt", "en_and_decrypt.py"),
            ("Compress/Decompress", "compress_decompress.py"),
            ("Split/Join Files", "file_splitter_joiner.py"),
            ("File Timestamps", "file_touch.py"),
            ("Secure Delete", "secure_delete.py")
        ],
        "Metadata": [
            ("Office Metadata", "office_meta_data_editor.py"),
            ("Media Tags", "tag_viewer_editor.py")
        ],
        "System": [
            ("File Permissions", "permissions_editor.py")
        ],
        "Administration": [
            ("Log Manager", "log_manager.py"),
            ("Settings", "settings_dialog.py")
        ]
    }
    
    # Track results
    results = {
        "success": [],
        "failure": []
    }
    
    # Test each tool
    for category, tool_list in tools.items():
        logging.info(f"\nTesting {category} tools:")
        logging.info("-" * 30)
        
        for tool_name, script_file in tool_list:
            if os.path.exists(script_file):
                if run_tool(script_file):
                    results["success"].append((category, tool_name))
                else:
                    results["failure"].append((category, tool_name))
            else:
                logging.error(f"Script file not found: {script_file}")
                results["failure"].append((category, tool_name))
            
            # Small delay between tests
            time.sleep(1)
    
    # Print summary
    logging.info("\n" + "=" * 50)
    logging.info("Test Summary:")
    logging.info("-" * 20)
    
    logging.info("\nSuccessful tests:")
    for category, tool in results["success"]:
        logging.info(f"✓ {category} - {tool}")
    
    if results["failure"]:
        logging.info("\nFailed tests:")
        for category, tool in results["failure"]:
            logging.info(f"✗ {category} - {tool}")
    
    total_tests = len(results["success"]) + len(results["failure"])
    success_rate = (len(results["success"]) / total_tests) * 100 if total_tests > 0 else 0
    
    logging.info("\nSummary:")
    logging.info(f"Total tests: {total_tests}")
    logging.info(f"Successful: {len(results['success'])}")
    logging.info(f"Failed: {len(results['failure'])}")
    logging.info(f"Success rate: {success_rate:.1f}%")
    logging.info("=" * 50)

if __name__ == "__main__":
    main()
