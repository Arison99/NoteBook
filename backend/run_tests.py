#!/usr/bin/env python3
"""
Test runner script for NoteBook backend tests.
Provides convenient commands for running different types of tests.
"""

import sys
import subprocess
import argparse
import os


def run_command(cmd, description=""):
    """Run a command and return the result"""
    if description:
        print(f"\n🔄 {description}")
        print("=" * 50)
    
    result = subprocess.run(cmd, shell=True, cwd=os.path.dirname(__file__))
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run NoteBook backend tests")
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--fast', action='store_true', help='Skip slow tests')
    parser.add_argument('--file', '-f', help='Run tests from specific file')
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd_parts = ['python', '-m', 'pytest']
    
    if args.verbose:
        cmd_parts.append('-v')
    
    if args.unit:
        cmd_parts.append('tests/unit')
        description = "Running unit tests"
    elif args.integration:
        cmd_parts.append('tests/integration')
        description = "Running integration tests"
    elif args.file:
        cmd_parts.append(f'tests/{args.file}')
        description = f"Running tests from {args.file}"
    else:
        cmd_parts.append('tests')
        description = "Running all tests"
    
    if args.fast:
        cmd_parts.extend(['-m', 'not slow'])
        description += " (excluding slow tests)"
    
    if args.coverage:
        cmd_parts.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])
        description += " with coverage"
    
    # Run the tests
    cmd = ' '.join(cmd_parts)
    return_code = run_command(cmd, description)
    
    if return_code == 0:
        print("\n✅ Tests completed successfully!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ Tests failed with exit code: {return_code}")
    
    return return_code


if __name__ == '__main__':
    sys.exit(main())