from markdown_pdf import MarkdownPdf, Section
import os

def convert():
    # Read the markdown file
    with open("Report_Concert_Tour_Analysis.md", "r", encoding="utf-8") as f:
        md_content = f.read()

    # Create PDF object WITHOUT an automatic Table of Contents (toc_level=0)
    # This prevents the "double list" at the start that can feel out of order.
    pdf = MarkdownPdf()
    
    # Add the content
    pdf.add_section(Section(md_content))
    
    # Save the output
    output_filename = "Report_Concert_Tour_Analysis.pdf"
    pdf.save(output_filename)
    print(f"Successfully converted to {output_filename} (Standard Order)")

if __name__ == "__main__":
    convert()
