#!/usr/bin/env python3
"""
Migration Script: Old TTS System → Chatterbox TTS
Helps transition from the old emotional_debate_system to the new M1 optimized Chatterbox system
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_status(message: str, status: str = "info"):
    """Print status message with appropriate emoji"""
    emoji_map = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️",
    }
    emoji = emoji_map.get(status, "ℹ️")
    print(f"{emoji} {message}")

def backup_old_files():
    """Create backup of important old files"""
    print_header("Creating Backup of Old System")
    
    backup_dir = Path("backup_old_system")
    if backup_dir.exists():
        print_status(f"Backup directory already exists: {backup_dir}", "warning")
        choice = input("Overwrite existing backup? (y/n): ")
        if choice.lower() != 'y':
            print_status("Backup cancelled", "warning")
            return False
        shutil.rmtree(backup_dir)
    
    backup_dir.mkdir()
    
    # Files to backup
    backup_files = [
        "requirements.txt",
        "main.py", 
        "src/",
        "config/",
        "tests/",
        ".env.example"
    ]
    
    for file_path in backup_files:
        if Path(file_path).exists():
            if Path(file_path).is_dir():
                shutil.copytree(file_path, backup_dir / file_path)
                print_status(f"Backed up directory: {file_path}", "success")
            else:
                shutil.copy2(file_path, backup_dir / file_path)
                print_status(f"Backed up file: {file_path}", "success")
        else:
            print_status(f"File not found (skipping): {file_path}", "warning")
    
    print_status(f"Backup created in: {backup_dir}", "success")
    return True

def analyze_old_config():
    """Analyze old configuration for migration insights"""
    print_header("Analyzing Old Configuration")
    
    config_insights = []
    
    # Check old requirements
    if Path("requirements.txt").exists():
        with open("requirements.txt", "r") as f:
            old_reqs = f.read()
            
        if "TTS" in old_reqs:
            config_insights.append("Found Coqui TTS dependency - will be replaced with Chatterbox")
        if "ollama" in old_reqs:
            config_insights.append("Found Ollama dependency - can be removed for voice-only mode")
        if "transformers" in old_reqs:
            config_insights.append("Found transformers - emotion detection may be migrated later")
        if "python-osc" in old_reqs:
            config_insights.append("Found OSC streaming - can be integrated with new system")
    
    # Check config files
    config_files = ["config/config.py", ".env.example"]
    for config_file in config_files:
        if Path(config_file).exists():
            config_insights.append(f"Found config file: {config_file} - review for migration")
    
    if config_insights:
        print("Configuration insights:")
        for insight in config_insights:
            print(f"  • {insight}")
    else:
        print_status("No specific configuration insights found", "info")
    
    return config_insights

def check_prerequisites():
    """Check if prerequisites for new system are met"""
    print_header("Checking Prerequisites")
    
    checks = []
    
    # Check macOS version for MPS
    try:
        import subprocess
        result = subprocess.run(['sw_vers', '-productVersion'], capture_output=True, text=True)
        macos_version = result.stdout.strip()
        print(f"macOS version: {macos_version}")
        
        # Parse version (e.g., "13.5.1" -> [13, 5, 1])
        version_parts = [int(x) for x in macos_version.split('.')]
        if version_parts[0] >= 12 and (version_parts[0] > 12 or version_parts[1] >= 3):
            checks.append(("macOS version for MPS", True))
        else:
            checks.append(("macOS version for MPS", False))
    except Exception:
        checks.append(("macOS version check", False))
    
    # Check conda availability
    conda_available = shutil.which('conda') is not None
    checks.append(("Conda availability", conda_available))
    
    # Check Python version
    python_version = sys.version_info
    python_ok = python_version.major == 3 and python_version.minor >= 9
    checks.append(("Python version (3.9+)", python_ok))
    
    # Print results
    all_good = True
    for check_name, status in checks:
        if status:
            print_status(f"{check_name}: OK", "success")
        else:
            print_status(f"{check_name}: FAILED", "error")
            all_good = False
    
    return all_good

def show_migration_plan():
    """Show the migration plan"""
    print_header("Migration Plan")
    
    steps = [
        "1. Backup old system files ✅ (completed above)",
        "2. Set up new conda environment with M1 optimization",
        "3. Install Chatterbox TTS and dependencies", 
        "4. Verify MPS support and performance",
        "5. Test voice cloning functionality",
        "6. Migrate any custom debate content",
        "7. Update project documentation"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print("\nDetailed migration commands:")
    print(f"  ./setup_m1_chatterbox.sh          # Complete M1 setup")
    print(f"  python verify_m1_setup.py         # Verify installation")
    print(f"  python art_installation_workflow.py  # Test new system")

def migrate_custom_content():
    """Help migrate custom content from old system"""
    print_header("Migrating Custom Content")
    
    # Check for custom debate content in old system
    custom_files = []
    
    # Look for debate-related files
    old_files_to_check = [
        "src/main.py",
        "main.py",
        "config/config.py"
    ]
    
    debate_keywords = ["debate", "statement", "dialogue", "conversation", "prompt"]
    
    for file_path in old_files_to_check:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read().lower()
                    if any(keyword in content for keyword in debate_keywords):
                        custom_files.append(file_path)
            except Exception:
                pass
    
    if custom_files:
        print("Found files that may contain custom debate content:")
        for file_path in custom_files:
            print(f"  • {file_path}")
        print("\nTo migrate custom content:")
        print("  1. Review these files for debate statements")
        print("  2. Copy relevant content to art_installation_workflow.py")
        print("  3. Update the debate_statements list")
    else:
        print_status("No custom debate content found to migrate", "info")

def show_next_steps():
    """Show next steps after migration"""
    print_header("Next Steps")
    
    next_steps = [
        "🚀 Run the setup script:",
        "   ./setup_m1_chatterbox.sh",
        "",
        "🔍 Verify the installation:",
        "   conda activate voice_m1_chatterbox",
        "   python verify_m1_setup.py",
        "",
        "🎭 Test the new system:",
        "   python art_installation_workflow.py",
        "",
        "📖 Read the new documentation:",
        "   README_CHATTERBOX.md",
        "",
        "🧹 Clean up old files (optional):",
        "   # After confirming new system works",
        "   rm -rf src/ config/ requirements.txt",
        "",
        "⚠️  Remember:",
        "   - Old virtual environment can be removed after testing",
        "   - Backup is preserved in backup_old_system/",
        "   - New system uses conda environment: voice_m1_chatterbox"
    ]
    
    for step in next_steps:
        print(step)

def main():
    """Main migration workflow"""
    print("🔄 MIGRATION TO CHATTERBOX TTS")
    print("="*50)
    print("This script helps migrate from the old emotional_debate_system")
    print("to the new M1 Max optimized Chatterbox TTS system")
    print("="*50)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print_status("Prerequisites not met. Please address issues above.", "error")
        return False
    
    # Step 2: Analyze old system
    analyze_old_config()
    
    # Step 3: Create backup
    print("\nWould you like to create a backup of the old system?")
    choice = input("This is recommended before migration (y/n): ")
    if choice.lower() == 'y':
        if not backup_old_files():
            print_status("Backup failed", "error")
            return False
    
    # Step 4: Show migration plan
    show_migration_plan()
    
    # Step 5: Check for custom content
    migrate_custom_content()
    
    # Step 6: Show next steps
    show_next_steps()
    
    print_status("Migration analysis complete!", "success")
    print("\n🎉 Ready to migrate to Chatterbox TTS!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration analysis failed: {e}")
        sys.exit(1)