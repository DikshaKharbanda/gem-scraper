import os
import fitz  # PyMuPDF
import json

# Dummy Gemini summarizer function (replace with real Gemini API call)
def summarize_pdf_with_gemini(text, bid_id):
    return {
        "title": f"Sample Title for Bid {bid_id}",
        "bid_number": bid_id,
        "dates": {
            "start_date": "2025-07-01",
            "end_date": "2025-07-15",
            "opening_date": "2025-07-16"
        },
        "scope": "Detailed scope of work and technical specifications.",
        "eligibility": "Eligibility criteria and required documents are listed.",
        "financial": {
            "boq": "Bill of Quantities details.",
            "emd": "Earnest Money Deposit details.",
            "payment_terms": "Payment will be made within 30 days."
        }
    }

# Extract text from PDF file
def extract_text_from_pdf(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

# Main processing for a sample folder with PDFs
def process_pdfs_for_summary(pdf_folder):
    summaries = []
    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            bid_id = file.replace(".pdf", "")
            pdf_path = os.path.join(pdf_folder, file)
            text = extract_text_from_pdf(pdf_path)
            if text.strip():
                summary = summarize_pdf_with_gemini(text, bid_id)
                summaries.append({"bid_id": bid_id, "summary": summary})
    return summaries

if __name__ == "__main__":
    input_folder = "gem_tender_results/pdfs"  # Update path if needed
    output_file = "gem_tender_results/summarized_tenders.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    result = process_pdfs_for_summary(input_folder)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Summarized tenders saved to: {output_file}")

