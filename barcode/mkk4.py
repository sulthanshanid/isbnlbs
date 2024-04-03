from reportlab.lib.pagesizes import A3
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from barcode import Code128
from barcode.writer import ImageWriter

# Function to generate barcode image with text label
def generate_barcode_with_text(barcode_value, text, filename):
    barcode = Code128(barcode_value, writer=ImageWriter())
    barcode.default_writer_options['module_height'] = 15  # Adjust height for readability
    barcode.default_writer_options['module_width'] = 0.5 * 15  # Adjust width
    barcode.default_writer_options['quiet_zone'] = 2
    barcode_path = f"{filename}"  # Manually specify the file extension
    barcode.save(barcode_path)  # Save barcode image
    return barcode_path+".png"

# Function to create A3 size PDF with barcodes and text labels
def generate_a3_pdf(barcode_range, filename):
    c = canvas.Canvas(filename, pagesize=A3)
    width, height = A3

    # Set initial position and dimensions
    x_margin = inch * 0.5
    y_margin = inch * 0.5
    barcode_width = 110  # Increase width by a factor of 1.2
    barcode_height = 40  # Increase height by a factor of 1.2
    x = x_margin
    y = height - y_margin

    # Calculate maximum number of rows and columns based on barcode size and page dimensions
    max_rows = int((height - 2 * y_margin) / (barcode_height + 20))
    max_columns = int((width - 2 * x_margin) / (barcode_width + 10))

    # Calculate maximum number of barcodes per page
    max_barcodes_per_page = max_rows * max_columns

    barcode_count = 0
    current_column = 0
    for code in barcode_range:
        if barcode_count % max_barcodes_per_page == 0 and barcode_count != 0:
            c.showPage()  # Start a new page
            x = x_margin
            y = height - y_margin
            current_column = 0

        if current_column == max_columns:
            x = x_margin
            y -= barcode_height + 20
            current_column = 0

        barcode_path = generate_barcode_with_text(code, code, f"{code.lower()}")  # Generate barcode with text label
        c.setFont("Helvetica", 6)  # Adjust font size for better fit
        c.drawString(x, y - barcode_height - 5, code)  # Add text label
        c.drawImage(barcode_path, x, y - barcode_height - 20, width=barcode_width, height=barcode_height)  # Use lowercase filename

        x += barcode_width + 10
        barcode_count += 1
        current_column += 1

    c.save()
    print(f"PDF generated: {filename}")

# Generate barcodes for the specified range
barcode_range = []
for i in range(1, 1401):
    barcode_range.append(f"CS{i:04d}")
for i in range(1, 230):
    barcode_range.append(f"CSTQ{i:03d}")

# Generate A3 PDF with barcodes and text labels
generate_a3_pdf(barcode_range, "book_barcodes.pdf")
