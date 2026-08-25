import subprocess
import os
import sys

def convert_pptx_to_images(pptx_path, output_dir="slide_images"):
    os.makedirs(output_dir, exist_ok=True)

    subprocess.run([
        "soffice", "--headless", "--convert-to", "pdf",
        "--outdir", output_dir, pptx_path
    ], check=True)

    pdf_name = os.path.splitext(os.path.basename(pptx_path))[0] + ".pdf"
    pdf_path = os.path.join(output_dir, pdf_name)

    print(f"Converted to PDF: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    pptx_file = sys.argv[1] if len(sys.argv) > 1 else "sample_slides.pptx"
    convert_pptx_to_images(pptx_file)