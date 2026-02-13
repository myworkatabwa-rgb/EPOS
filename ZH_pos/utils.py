import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64


def generate_barcode_base64(code):
    Code128 = barcode.get_barcode_class('code128')

    buffer = BytesIO()

    barcode_obj = Code128(code, writer=ImageWriter())

    barcode_obj.write(buffer, options={
        "module_width": 0.2,
        "module_height": 15,
        "font_size": 12,
        "text_distance": 2,
        "quiet_zone": 2,
    })

    barcode_base64 = base64.b64encode(buffer.getvalue()).decode()

    return barcode_base64
