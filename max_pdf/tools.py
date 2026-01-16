import subprocess
import os
from typing import List

def list_pdf_files(directory: str = ".") -> List[str]:
    # Return all pdf files in the curr director
    try:
        files = os.listdir(directory)
        pdf_files = [f for f in files if f.endswith(".pdf")]
        return pdf_files
    except Exception as e:
        return [f"Error listing files: {str(e)}"]
    
def get_pdf_info(filepath: str) -> dict:
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

    

                
        
        
        