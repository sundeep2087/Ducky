import ast
import glob
import json
import os
import re
import textwrap
from hashlib import md5
from typing import List
from typing import Optional
from typing import Tuple

from autogen import Agent, ConversableAgent
from config import UNKNOWN, WORKING_DIR, CODE_BLOCK_PATTERN


# Helper function to generate the appropriate preamble for each language
def generate_preamble(lang: str, filename: str) -> str:
    if lang == "python":
        return f"# filename: {filename}"
    elif lang == "html":
        return f"<!-- filename: {filename} -->"
    elif lang == "css":
        return f"/* filename: {filename} */"
    elif lang == "javascript":
        return f"// filename: {filename}"
    elif lang == "markdown":
        return f"<!-- filename: {filename} -->"
    elif lang == "yaml":
        return f"# filename: {filename}"
    return ""


def extract_code(
        text: str, pattern: str = CODE_BLOCK_PATTERN,
) -> List[Tuple[str, str]]:
    """
    Extract code blocks from a text and format preambles as comments.
    This function now supports various types of code (Python, HTML, CSS, JavaScript, Markdown, YAML).
    Filters out non-code parts like headings and descriptions.
    """
    matches = re.findall(pattern, text, flags=re.DOTALL)

    result = []

    for match in matches:
        preamble, lang, code = match
        filename_line = ""
        preamble_lines = []

        # Process each line in the preamble
        for line in preamble.split("\n"):
            line_stripped = line.strip()

            # Check for filename comment format and capture it
            if line_stripped.startswith(("# filename", "// filename", "<!-- filename", "/* filename")):
                if not filename_line:  # Only capture the first occurrence
                    filename_line = line_stripped
            else:
                # Exclude non-code parts like page titles, markdown, or page descriptions
                if line_stripped and not line_stripped.startswith(("#", "//", "<!--", "/*")):
                    preamble_lines.append(f"# {line}")

        # Concatenate the processed preamble lines with newlines
        commented_preamble = "\n".join(preamble_lines)

        # Concatenate the filename line (if any), the commented preamble, and the code, with newlines in between
        full_code = "\n".join(filter(None, [filename_line, commented_preamble, code]))

        result.append((lang, full_code))

    if not result:
        result.append((UNKNOWN, text))

    return result


def _get_function_signature(function: ast.FunctionDef) -> str:
    """
    Construct the function signature from the function definition, including type annotations.
    """
    func_name = function.name
    args = []
    for arg in function.args.args:
        arg_name = arg.arg
        if arg.annotation:
            arg_name += f": {ast.unparse(arg.annotation)}"
        args.append(arg_name)

    defaults_offset = len(args) - len(function.args.defaults)
    for i, default in enumerate(function.args.defaults):
        args[i + defaults_offset] += f"={ast.unparse(default)}"

    return_annotation = ""
    if function.returns:
        return_annotation = f" -> {ast.unparse(function.returns)}"

    args_str = ", ".join(args)
    return f"{func_name}({args_str}){return_annotation}"


def _get_public_functions(file_path: str):
    """
    Extract the public functions and their signatures from a Python file.
    """
    with open(file_path, "r", encoding='utf-8') as source:
        node = ast.parse(source.read())

    functions = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
            functions.append(_get_function_signature(item))
        elif isinstance(item, ast.ClassDef):
            for class_item in item.body:
                if isinstance(class_item, ast.FunctionDef) and not class_item.name.startswith("_"):
                    functions.append(f"{item.name}.{_get_function_signature(class_item)}")

    return functions


def summarize_files(working_folder: str) -> str:
    """
    Summarizes each code file in the specified folder (including Python, HTML, CSS, JS, MD, and YAML).
    """
    markdown_summary = ""

    for subdir, _, files in os.walk(working_folder):
        for file in files:
            if file.endswith((".py", ".html", ".css", ".js", ".md", ".yaml", ".yml", ".javascript")):
                file_path = os.path.join(subdir, file)

                # Summarize based on file type
                if file.endswith(".py"):
                    public_functions = _get_public_functions(file_path)
                    markdown_summary += f"## {file_path}\n"
                    if public_functions:
                        for signature in public_functions:
                            markdown_summary += f"- `{signature}`\n"
                    else:
                        markdown_summary += "No public methods.\n"

                elif file.endswith((".html", ".css", ".js", ".md", ".yaml", ".yml", ".javascript")):
                    markdown_summary += f"## {file_path}\n"
                    with open(file_path, "r", encoding='utf-8') as f:
                        content = f.read()
                    markdown_summary += f"```{file.split('.')[-1]}\n{content}\n```\n"
                markdown_summary += "\n"

    return markdown_summary


def sanitize_filename(filename: str) -> str:
    """
    Sanitize the filename to ensure it doesn't contain invalid characters for the operating system.
    Removes characters like *, ?, <, >, |, etc.
    """
    return re.sub(r'[ <>:"\\|?*]', '', filename)

def save_code(
        code: str = None,
        work_dir: Optional[str] = None,
        lang: Optional[str] = "python",
) -> str:
    """
    Save the code in a working directory, supporting multiple languages (Python, HTML, CSS, JavaScript, Markdown, YAML).
    This function determines the correct filename extension based on the language and saves the file accordingly.
    It can handle different comment syntaxes (e.g., # for Python, // for JavaScript, <!-- for HTML).
    """
    # Define comment patterns for various languages
    comment_patterns = {
        'python': r"# filename: ([^\n]+)",
        'javascript': r"// filename: ([^\n]+)",
        'html': r"<!-- filename: ([^\n]+) -->",
        'css': r"/* filename: ([^\n]+) */",
        'markdown': r"<!-- filename: ([^\n]+) -->",  # Markdown may also use HTML-style comments for metadata
        'yaml': r"# filename: ([^\n]+)",  # YAML typically uses # for comments
    }
    pattern = comment_patterns.get(lang, r"# filename: ([^\n]+)")

    filename_match = re.findall(pattern, code)
    if filename_match:
        filename = filename_match[0]
    else:
        code_hash = md5(code.encode()).hexdigest()
        filename = f"tmp_code_{code_hash}.{lang}"

    filename = sanitize_filename(filename)
    work_dir = work_dir or WORKING_DIR
    filepath = os.path.join(work_dir, filename)
    file_dir = os.path.dirname(filepath)
    os.makedirs(file_dir, exist_ok=True)

    # Save the code to the file
    if code is not None:
        with open(filepath, "w", encoding="utf-8") as fout:
            fout.write(code)

    return filename


def save_code_files(llm_message: str, work_dir: Optional[str] = None) -> List[str]:
    """
    Save all extracted code files (Python, HTML, CSS, JS, MD, YAML).
    """
    filenames = []
    code_files = extract_code(llm_message)

    for lang, code_block in code_files:
        if lang in ['python', 'html', 'css', 'javascript', 'markdown', 'yaml']:
            filename = save_code(code_block, work_dir, lang)
            filenames.append(filename)

    return filenames


def clear_working_dir(work_dir: Optional[str] = None, filename_wildcard: str = '*.py') -> None:
    """
    Clears files from the specified working directory.
    """
    work_dir = work_dir or WORKING_DIR

    if os.path.exists(work_dir) and os.path.isdir(work_dir):
        # Find all supported files in the working directory and subdirectories
        files = glob.glob(os.path.join(work_dir, '**', filename_wildcard), recursive=True)

        for file_path in files:
            try:
                os.remove(file_path)
                print(f"Deleted {file_path}")

                # Remove the directory if it's empty
                dir_path = os.path.dirname(file_path)
                if not os.listdir(dir_path):
                    os.removedirs(dir_path)
                    print(f"Removed directory {dir_path}")

            except Exception as e:
                print(f"Could not delete {file_path} due to {e}")
    else:
        print("The specified path does not exist or it is not a directory")
