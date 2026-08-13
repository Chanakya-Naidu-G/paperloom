from app.ingestion.parser import parse_pdf
def load_document(file_path:str,extension: str):
    if(extension==".pdf"):
        return parse_pdf(file_path)
    raise ValueError("Unsopported file type")