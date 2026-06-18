"""Python script to list all project files - for verification"""

import os
import json

def count_files():
    stats = {
        'python_files': 0,
        'javascript_files': 0,
        'config_files': 0,
        'documentation': 0,
        'total_files': 0,
    }
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden dirs and node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        for file in files:
            if file.startswith('.'):
                continue
            
            stats['total_files'] += 1
            
            if file.endswith('.py'):
                stats['python_files'] += 1
            elif file.endswith(('.jsx', '.js')):
                stats['javascript_files'] += 1
            elif file.endswith(('.json', '.yml', '.yaml', '.env')):
                stats['config_files'] += 1
            elif file.endswith(('.md', '.txt')):
                stats['documentation'] += 1
    
    return stats

if __name__ == '__main__':
    stats = count_files()
    print("=" * 50)
    print("TRINETRA Project Statistics")
    print("=" * 50)
    for key, value in stats.items():
        print(f"{key:<20}: {value:>5}")
    print("=" * 50)
