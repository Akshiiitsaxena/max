import subprocess
import os
from typing import Dict, List, Union

from max_pdf.ui import global_status, console

# helpers

def _resolve_filename(filename: str) -> str:
    # exact match
    if os.path.exists(filename):
        return filename
    
    # without extension
    if os.path.exists(f"{filename}.pdf"):
        return f"{filename}.pdf"
    
    try:
        all_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
        
        # Split input into tokens: "test rotate file" -> ["test", "rotate", "file"]
        query_tokens = filename.lower().replace("_", " ").split()
        
        candidates = []
        for f in all_files:
            f_lower = f.lower().replace("_", " ")
            if all(token in f_lower for token in query_tokens):
                candidates.append(f)
        
        if len(candidates) == 1:
            return candidates[0]
            
    except Exception:
        pass
    
    return filename

def _validate_inputs(filepaths: List[str]) -> Union[bool, str]:
    # check if input files exists
    missing = []
    
    for fp in filepaths:
        if not os.path.exists(fp):
            missing.append(fp)
    
    if missing:
        return f"Error: these files not found: {missing}"
    
    return True

def _verify_output(output_path: str):
    if not os.path.exists(output_path):
        return f"ERROR: tool ran but output file path {output_path} not created."
    
    return True

# tools

def list_pdf_files(directory: str = ".") -> List[str]:
    # Return all pdf files in the curr director
    try:
        files = os.listdir(directory)
        pdf_files = [f for f in files if f.endswith(".pdf")]
        return pdf_files
    except Exception as e:
        return [f"Error listing files: {str(e)}"]
    
def get_pdf_info(filepath: str) -> dict:
    filepath = _resolve_filename(filename=filepath)
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    
    try:
        result = subprocess.run(
            ["pdfcpu", "info", filepath],
            capture_output=True,
            text=True,
            check=True,
        )
        
        output = result.stdout
        
        info = {
            "filepath": filepath,
            "pages": 0,
            "encrypted": "encrypted: yes" in output.lower()
        }
        
        # get page count
        for line in output.splitlines():
            if "Page count:" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    info["pages"] = int(parts[1].strip())
        
        return info
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to read PDF: {e.stderr}"}


def rotate_pages(filepath: str, output_path: str, pages: str, angle: int) -> str:
    try:
        cmd = ["pdfcpu", "rotate", "-pages", pages, filepath, str(angle), output_path]
        
        # check param throws err if result.returncode is non-zero
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"status": "success", "output_file": output_path}
    
    except subprocess.CalledProcessError as e:
        return {"status": "error", "details": e.stderr.strip()}
        
    except Exception as e:
        return {"status": "error", "details": str(e)}

def remove_pages(filepath: str, output_path: str, pages: str) -> Dict:
    try:
        cmd = ["pdfcpu", "pages", "remove", "-pages", pages, filepath, output_path]
    
        # check param throws err if result.returncode is non-zero
        subprocess.run(cmd, capture_output=True, text=True)
        return {"status": "success", "output_file": output_path}
    
    except subprocess.CalledProcessError as e:
        return {"status": "error", "details": e.stderr.strip()}    
   
    except Exception as e:
        return {"status": "error", "details": str(e)}

def merge_pdfs(output_path: str, input_paths: List[str]) -> Dict:
    cleaned_paths = [_resolve_filename(filename) for filename in input_paths]
    if not _validate_inputs(cleaned_paths):
        return {"error": "inputs not valid"}
    
    try:
        cmd = ["pdfcpu", "merge", output_path] + cleaned_paths
        subprocess.run(cmd, capture_output=True, text=True)
        return {"status": "success", "output_file": output_path}
    
    except subprocess.CalledProcessError as e:
        return {"status": "error", "details": e.stderr.strip()}  
    
    except Exception as e:
        return {"status": "error", "details": str(e)}

def ask_human(question: str) -> str:
    """Asks the human user for a clarifying question."""
    
    global_status.stop()
    response = console.input(f"\n[bold dark_orange]🤖 Max:[/bold dark_orange] {question}\n> ")
    global_status.start()
    
    return response