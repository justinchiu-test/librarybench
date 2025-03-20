import os
import ast
import argparse
import subprocess
import tempfile
import shutil
import textwrap

global activate_breakpoint

def clone_repo(repo_url, dest_dir):
    """Clone a GitHub repository into dest_dir."""
    subprocess.run(["git", "clone", repo_url, dest_dir], check=True)

def get_function_source(file_path, function_name):
    """
    Parse the file with ast to extract the source code of the given function.
    Returns the function source code as a string, the start and end line numbers,
    and the list of parameter names.
    """
    with open(file_path, "r") as f:
        source = f.read()
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            start_line = node.lineno - 1
            end_line = getattr(node, 'end_lineno', None)
            if end_line is None:
                end_line = node.body[-1].lineno
            source_lines = source.splitlines()
            func_source = "\n".join(source_lines[start_line:end_line])
            # Extract parameter names (naïvely ignoring *args, **kwargs)
            param_names = [arg.arg for arg in node.args.args]
            return func_source, start_line, end_line, param_names
    return None, None, None, None

def remove_function_from_file(file_path, function_name):
    """
    Remove the function definition of `function_name` from the file.
    This approach blanks out the lines of the function definition.
    """
    with open(file_path, "r") as f:
        lines = f.readlines()
    tree = ast.parse("".join(lines))
    new_lines = lines.copy()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            start = node.lineno - 1
            end = getattr(node, 'end_lineno', None)
            if end is None:
                end = node.body[-1].lineno
            for i in range(start, end):
                new_lines[i] = ""  # blank out these lines
            break
    new_source = "".join(new_lines)
    with open(file_path, "w") as f:
        f.write(new_source)

class FunctionInliner(ast.NodeTransformer):
    def __init__(self, function_name, inline_body, param_names):
        """
        :param function_name: The name of the function to inline.
        :param inline_body: List of AST nodes corresponding to the function's body.
        :param param_names: List of parameter names for the function.
        """
        self.function_name = function_name
        self.inline_body = inline_body  # a list of AST nodes
        self.param_names = param_names
        self.num_inlined = 0

    def visit_Module(self, node):
        # Ensure we process all nodes in the module.
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        # Process the body of the class (which may contain methods where calls occur)
        self.generic_visit(node)
        return node

    def visit_Expr(self, node):
        """
        Look for expression statements that are a call to our target function.
        Replace the call with a series of assignment nodes (for parameters)
        followed by the function body nodes.
        """
        if isinstance(node.value, ast.Call):
            call = node.value

            # Debug: print the call node structure
            print("DEBUG: Found call node:", ast.dump(call, indent=2))

            # Check for both direct calls (e.g., func()) and attribute calls (e.g., self.func())
            if (isinstance(call.func, ast.Name) and call.func.id == self.function_name) or \
               (isinstance(call.func, ast.Attribute) and call.func.attr == self.function_name):
                # Check that the number of arguments matches.
                if len(call.args) != len(self.param_names):
                    print("DEBUG: Argument count does not match for", self.function_name)
                    return node  # skip inlining if counts don't match
                self.num_inlined += 1

                # Create assignment nodes mapping parameters to the call's arguments.
                assign_nodes = []
                for param, arg in zip(self.param_names, call.args):
                    assign = ast.Assign(
                        targets=[ast.Name(id=param, ctx=ast.Store())],
                        value=arg
                    )
                    assign_nodes.append(assign)

                # Prepare a copy of the inline body, converting returns into expression statements.
                new_body = []
                for stmt in self.inline_body:
                    if isinstance(stmt, ast.Return):
                        if stmt.value is not None:
                            new_body.append(ast.Expr(value=stmt.value))
                    else:
                        new_body.append(stmt)

                # Replace the original call (as a statement) with our inlined nodes.
                return assign_nodes + new_body

        return self.generic_visit(node)


def inline_function_calls_in_file(file_path, function_name, function_source, param_names):
    """
    Inline calls to `function_name` in the given file using AST.
    The function source (including its body) is parsed, and for each call
    to the function (as a standalone statement), the call is replaced with:
      1. Assignments mapping parameters to the arguments.
      2. The inlined function body.
    Returns the number of inlined occurrences.
    """
    with open(file_path, "r") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return 0

    # Parse the function source to extract its AST body.
    func_tree = ast.parse(function_source)
    func_def = func_tree.body[0]  # should be an ast.FunctionDef
    inline_body = func_def.body  # list of AST nodes from the function body

    # Transform the AST, replacing call sites with inline code.
    inliner = FunctionInliner(function_name, inline_body, param_names)
    if activate_breakpoint: breakpoint()
    new_tree = inliner.visit(tree)
    ast.fix_missing_locations(new_tree)

    # Generate new source code.
    try:
        new_source = ast.unparse(new_tree)
    except Exception as e:
        print(f"Error unparsing AST for {file_path}: {e}")
        return 0

    with open(file_path, "w") as f:
        f.write(new_source)

    return inliner.num_inlined

def process_repository(repo_path, function_file, function_name):
    """
    Locate the utils.py file in the repository, extract the specified function,
    inline its calls in all Python files using AST, and remove its definition.
    Returns a tuple (num_inlined, total_lines_added).
    """
    global activate_breakpoint
    function_source, start, end, param_names = get_function_source(function_file, function_name)
    if not function_source:
        print(f"Function {function_name} not found in utils.py")
        return 0, 0

    num_inlined = 0
    # Walk through all .py files in the repository.
    for root, _, files in os.walk(repo_path):
        for file in files:
            if "style_transformation.py" in file: activate_breakpoint = True
            else: activate_breakpoint = False
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Skip the file where the function is defined.
                if os.path.abspath(file_path) == os.path.abspath(function_file):
                    continue
                num_inlined += inline_function_calls_in_file(file_path, function_name, function_source, param_names)
    
    # Remove the function definition from utils.py.
    remove_function_from_file(function_file, function_name)
    num_lines_in_function = end - start
    return num_inlined, num_lines_in_function * num_inlined

def find_util_functions(repo_path):
    """
    Hunt for a utils.py file in the repository (in any directory),
    and return a list of all top-level function names defined in it.
    """
    utils_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file == "utils.py":
                utils_files.append(os.path.join(root, file))
    if not utils_files:
        return []
    
    function_names = []
    for utils_path in utils_files:
        with open(utils_path, "r") as f:
            source = f.read()
        try:
            tree = ast.parse(source)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    function_names.append((utils_path, node.name))
        except Exception as e:
            print(f"Error parsing {utils_path}: {e}")
    return function_names

def get_args():
    parser = argparse.ArgumentParser(
        description="Inline selected library functions from utils.py into their call sites using AST."
    )
    parser.add_argument("repo", help="GitHub repository URL or local path")
    args = parser.parse_args()
    return args

def get_args():
    parser = argparse.ArgumentParser(
        description="Inline selected library functions from utils.py into their call sites."
    )
    parser.add_argument("--repo", help="GitHub repository URL or local path")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    global activate_breakpoint
    activate_breakpoint = False
    args = get_args()

    repo_path = args.repo
    temp_dir = os.path.join(os.getcwd(), "tmp")
    os.makedirs(temp_dir, exist_ok=True)

    # If the repo argument is a URL, clone it to a temporary directory.
    overwrite = False
    if repo_path.startswith("http"):
        repo_name = os.path.basename(args.repo).rstrip()
        if repo_name.endswith(".git"): repo_name = repo_name[:-len(".git")]
        repo_path = os.path.join(temp_dir, repo_name)
        try:
            print(f"Cloning repository into {repo_path}...")
            clone_repo(args.repo, repo_path)
        except:
            print(f"Cannot clone {args.repo}... already exists. Using existing version.")
    print(repo_path)
    function_options = find_util_functions(repo_path)
    if not function_options:
        print("No utility functions found in any utils.py file.")
    else:
        do_another = True
        while do_another and function_options:
            print("Available functions to inline:")
            function_options = list(function_options)
            for idx, (filename, func) in enumerate(function_options):
                print(f"- ({idx}) {os.path.basename(filename)}::{func}")
            selected_idx = input("Which function would you like to inline? (num)\n").strip()
            try: selected_idx = int(selected_idx)
            except: 
                print("Sorry, couldn't parse. Type and integer in the range.")
                continue
            (selected_filename, selected_function) = function_options[selected_idx]
            num_inlined, num_lines_increased = process_repository(repo_path, selected_filename, selected_function)
            print(f"Inlined {selected_function} into {num_inlined} places, increasing repo length by {num_lines_increased} lines.")
            function_options.pop(selected_idx)
            if function_options:
                do_another = input("Inline another? [y/]: ").strip().lower() == 'y'
            else:
                do_another = False


    print(f"Find your newly inlined repository at {repo_path}")
    # If using a temporary directory, you might want to inspect the repository before cleanup.
