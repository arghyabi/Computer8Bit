#!/usr/bin/env python3
"""
Version validation script for semantic versioning compliance.
Validates that version changes follow semantic versioning rules and build number requirements.
"""

import subprocess
import sys
import os
import yaml


def parse_version(version_string):
    """Parse version string into components."""
    parts = version_string.split('.')
    if len(parts) != 4:
        return None
    try:
        return {
            'major': int(parts[0]),
            'minor': int(parts[1]),
            'patch': int(parts[2]),
            'build': int(parts[3])
        }
    except ValueError:
        return None


def get_old_version(base_ref, component_name=None):
    """Get version from base branch."""
    try:
        old_config = subprocess.check_output(
            ['git', 'show', f'{base_ref}:Config.yaml'],
            text=True
        )
        old_data = yaml.safe_load(old_config)
        
        if component_name:
            return old_data['Components'][component_name]
        else:
            return old_data['Version']['MainVersion']
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Error getting old Config.yaml: {e}")
        sys.exit(1)


def get_new_version(component_name=None):
    """Get version from current branch."""
    try:
        with open('Config.yaml', 'r') as f:
            new_data = yaml.safe_load(f)
            
        if component_name:
            return new_data['Components'][component_name]
        else:
            return new_data['Version']['MainVersion']
    except Exception as e:
        print(f"ERROR: Error reading new Config.yaml: {e}")
        sys.exit(1)


def validate_version_change(old_version, new_version, component_name):
    """Validate version change according to semantic versioning rules."""
    
    old_v = parse_version(old_version)
    new_v = parse_version(new_version)
    
    if not old_v or not new_v:
        print(f"ERROR: Invalid version format for {component_name}!")
        print(f"   Old: {old_version}")
        print(f"   New: {new_version}")
        return False
    
    # Check if versions are identical
    if old_version == new_version:
        print(f"ERROR: {component_name} was not updated!")
        print(f"   Current: {old_version}")
        print(f"   Required: At least one of major/minor/patch must change AND build must change")
        return False
    
    # Check if at least one of major/minor/patch changed
    semantic_changed = (
        old_v['major'] != new_v['major'] or
        old_v['minor'] != new_v['minor'] or
        old_v['patch'] != new_v['patch']
    )
    
    # Check if build changed
    build_changed = old_v['build'] != new_v['build']
    
    if not semantic_changed:
        print(f"ERROR: {component_name} build-only update detected!")
        print(f"   Old: {old_version}")
        print(f"   New: {new_version}")
        print(f"   At least one of major/minor/patch must be updated along with build")
        return False
    
    if not build_changed:
        print(f"ERROR: {component_name} build number was not updated!")
        print(f"   Old: {old_version}")
        print(f"   New: {new_version}")
        print(f"   Build number MUST be updated with every change")
        return False
    
    # Semantic versioning rules
    if old_v['major'] != new_v['major']:
        if new_v['minor'] != 0 or new_v['patch'] != 0:
            print(f"ERROR: {component_name} semantic versioning violation!")
            print(f"   Old: {old_version}")
            print(f"   New: {new_version}")
            print(f"   When major version changes, minor and patch must be reset to 0")
            print(f"   Expected: {new_v['major']}.0.0.{new_v['build']}")
            return False
    elif old_v['minor'] != new_v['minor']:
        if new_v['patch'] != 0:
            print(f"ERROR: {component_name} semantic versioning violation!")
            print(f"   Old: {old_version}")
            print(f"   New: {new_version}")
            print(f"   When minor version changes, patch must be reset to 0")
            print(f"   Expected: {new_v['major']}.{new_v['minor']}.0.{new_v['build']}")
            return False
    
    print(f"SUCCESS: {component_name} version updated correctly")
    print(f"   Old: {old_version}")
    print(f"   New: {new_version}")
    return True


def main():
    """Main validation function."""
    if len(sys.argv) < 3:
        print("Usage: validate_version.py <base_ref> <component_name|MainVersion>")
        sys.exit(1)
    
    base_ref = sys.argv[1]
    component_name = sys.argv[2]
    
    # Get versions
    if component_name == "MainVersion":
        old_version = get_old_version(base_ref)
        new_version = get_new_version()
    else:
        old_version = get_old_version(base_ref, component_name)
        new_version = get_new_version(component_name)
    
    # Validate
    if validate_version_change(old_version, new_version, component_name):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
