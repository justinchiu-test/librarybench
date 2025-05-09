#!/usr/bin/env python3
import os
import sys
import re
import glob
import shutil
import logging

# ——— UNUSED@!! helper to fix imports in the moved file ———
def _update_local_imports(destination_path, theoretical_original_path, persona):
    """
    Update import statements in files that have been reorganized.
    - Test files: {LIBRARY}_{PERSONA}_o4-mini_iterative/**/test_*.py --> {LIBRARY}/unified/tests/{PERSONA}_test_*.py
    - Source files: {LIBRARY}_{PERSONA}_o4-mini_iterative/**/*.py --> {LIBRARY}/{PERSONA}/**/*.py
    
    Args:
        destination_path: Path where the file has been copied to
        theoretical_original_path: Path where the file would have been in the new structure (for reference)
        persona: The persona name for the file
    """
    if not os.path.exists(destination_path):
        return

    # Extract the library name from the path
    path_parts = destination_path.split(os.sep)
    library = path_parts[path_parts.index(persona) - 1] if persona in path_parts else None
    
    if not library:
        logger.warning(f"Could not determine library for {destination_path}")
        return
        
    # Get all Python files in the library persona directory to identify local modules
    library_persona_dir = os.path.join(os.getcwd(), library, persona)
    library_files = []
    
    if os.path.exists(library_persona_dir):
        for root, _, files in os.walk(library_persona_dir):
            for file in files:
                if file == "__init__.py": continue 
                if file.endswith('.py'):
                    # Get module name without .py extension
                    module_name = os.path.splitext(file)[0]
                    subdir = os.path.relpath(root, library_persona_dir)
                    if subdir != ".": module_name = f"{subdir}.{module_name}"
                    library_files.append(module_name)
    
    # Get all test files
    tests_dir = os.path.join(os.getcwd(), library, "unified", "tests")
    test_files = []
    
    if os.path.exists(tests_dir):
        for root, _, files in os.walk(tests_dir):
            for file in files:
                if file.endswith('.py') and file.startswith(f"{persona}_test_"):
                    # Get module name without .py extension and persona prefix
                    test_name = os.path.splitext(file)[0][len(persona)+1:]  # Remove persona_ prefix
                    test_files.append(test_name)
    
    with open(destination_path, 'r') as f:
        content = f.read()
    
    # Find import statements (both regular imports and from imports)
    import_pattern = re.compile(r'(?m)^(from\s+|import\s+)([.\w]+)')
    matches = import_pattern.findall(content)
    
    # Check if this is a test file
    is_test_file = 'unified/tests' in destination_path and destination_path.endswith('.py')
    
    modified_content = content
    for match in matches:
        import_type, module_path = match
        # Skip imports that already have the right prefix
        if module_path.startswith(f"{library}.") or module_path.startswith(f"{library}.unified."):
            continue
            
        # Handle local imports - need to determine if it's a module from this project
        # module_first_part = module_path.split('.')[0]
        
        # Check if this is a local import by looking at our file structure
        is_local = False
        breakpoint()
        if module_path in library_files:
            is_local = True
        elif module_path.startswith('test_') and module_path in test_files:
            is_local = True
        elif module_path.startswith('.'):  # Relative import is always local
            is_local = True
        
        # Skip if it's not a local import
        if not is_local and not module_path.startswith('.'):
            continue
            
        # For test files, we need to update imports to point to the unified structure
        if is_test_file:
            # If importing another test file or a source module
            if module_path.startswith('test_'):
                # Update to use the unified test structure
                old_import = f"{import_type}{module_path}"
                new_import = f"{import_type}{library}.unified.tests.{persona}_{module_path}"
                modified_content = modified_content.replace(old_import, new_import)
            else:
                # Importing from source, add the persona path
                old_import = f"{import_type}{module_path}"
                new_import = f"{import_type}{library}.{persona}.{module_path}"
                modified_content = modified_content.replace(old_import, new_import)
        else:
            # For source files, update imports to include the library and persona
            if not module_path.startswith('.'):
                old_import = f"{import_type}{module_path}"
                # If it's importing a test, point to the unified test structure
                if 'test_' in module_path:
                    new_import = f"{import_type}{library}.unified.tests.{persona}_{module_path}"
                else:
                    new_import = f"{import_type}{library}.{persona}.{module_path}"
                modified_content = modified_content.replace(old_import, new_import)
            else:
                # Relative imports - need special handling based on file location
                # For now, keep them as is, as they might still work depending on package structure
                pass
    
    # Write the updated content back to the file
    if modified_content != content:
        with open(destination_path, 'w') as f:
            f.write(modified_content)
        logger.info(f"Updated imports in {destination_path}")

def main():
    repo_root = os.getcwd()
    libs = [
        "workflow_orchestration",
        "data_encoder",
        "dependency_resolver",
        "document_editor",
    ]

    for lib in libs:
        pattern = f"{lib}_*_o4-mini_iterative"
        for src_dir in glob.glob(pattern):
            if not os.path.isdir(src_dir):
                continue

            persona = src_dir[len(lib)+1 : -len("_o4-mini_iterative")]
            logger.info(f"Reorganizing {src_dir!r} for persona {persona!r}")

            persona_root = os.path.join(repo_root, lib, persona)
            tests_root   = os.path.join(repo_root, lib, "unified", "tests")
            os.makedirs(persona_root, exist_ok=True)
            os.makedirs(tests_root, exist_ok=True)

            # walk all subdirs
            for dirpath, dirnames, filenames in os.walk(src_dir):
                rel_dir = os.path.relpath(dirpath, src_dir)  # "." for root
                for fname in filenames:
                    if not (fname.endswith(".py") or fname.endswith(".md")):
                        continue
                    # fix imports
                    src_path = os.path.join(dirpath, fname)

                    # decide dest subfolder & name
                    if fname.startswith("test_") and fname.endswith(".py"):
                        # dest_sub = os.path.join(tests_root, rel_dir)
                        # os.makedirs(dest_sub, exist_ok=True)
                        # dest_name = f"{persona}_{fname}"
                        dest_name = f'{fname[:len("test_")]}{persona}_{fname[len("test_"):]}' 
                        dest_path = os.path.join(tests_root, dest_name)
                        # dest_path = os.path.join(dest_sub, dest_name)
                        # theoretical_original_path = os.path.join(persona_root, rel_dir, dest_name)
                    else:
                        dest_sub = os.path.join(persona_root, rel_dir)
                        os.makedirs(dest_sub, exist_ok=True)
                        dest_path = os.path.join(dest_sub, fname)
                        # theoretical_original_path = dest_path  # Source files keep the same structure

                    logger.info(f" Moving {src_path!r} → {dest_path!r}")
                    shutil.copyfile(src_path, dest_path)
                    
                    # Update imports after copying file to destination
                    # _update_local_imports(dest_path, theoretical_original_path, persona)
            shutil.rmtree(src_dir)
    logger.info("All done.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)
    main()
