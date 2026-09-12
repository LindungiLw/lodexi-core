import io
import fitz  # PyMuPDF
import docx

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from a file based on its extension.
    Supported: .txt, .pdf, .docx
    """
    ext = filename.lower().split('.')[-1]
    
    if ext == 'txt':
        return file_bytes.decode('utf-8', errors='ignore')
        
    elif ext == 'pdf':
        text = ""
        # PyMuPDF can read from memory buffer
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text() + "\n"
        return text
        
    elif ext == 'docx':
        text = ""
        # python-docx needs a file-like object
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
        
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
