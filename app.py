from flask import Flask, request, send_file, render_template_string
from pdf2docx import Converter
from docx import Document
from PIL import Image, ImageDraw
import easyocr
from pdf2image import convert_from_path
import os
import uuid
import textwrap
import zipfile

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>CloudConverterX</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: #f0f8ff;
      text-align: center;
      padding-top: 40px;
    }
    form {
      background: #ffffff;
      padding: 30px;
      display: inline-block;
      border-radius: 12px;
      box-shadow: 0 0 12px rgba(0,0,0,0.2);
    }
    h1 {
      color: #333366;
    }
    select, input[type="file"], button {
      font-size: 16px;
      padding: 10px;
      margin: 10px;
    }
    button {
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 6px;
    }
  </style>
</head>
<body>
  <h1>Cloud File Converter</h1>
  <form action="/convert" method="POST" enctype="multipart/form-data">
    <label><b>Select File:</b></label><br>
    <input type="file" name="file" required><br><br>

    <label><b>Conversion Type:</b></label><br>
    <select name="option" required>
      <option value="pdf2docx">PDF to Word</option>
      <!-- <option value="docx2pdf">Word to PDF (Disabled on Linux)</option> -->
      <option value="image2word">Image to Word (OCR)</option>
      <option value="word2image">Word to Image</option>
      <option value="image2pdf">Image to PDF</option>
      <option value="pdf2image">PDF to Image</option>
    </select><br><br>

    <button type="submit">Convert</button>
  </form>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/convert', methods=['POST'])
def convert():
    try:
        file = request.files['file']
        option = request.form['option']
        filename = str(uuid.uuid4()) + "_" + file.filename
        file.save(filename)

        if option == 'pdf2docx':
            output = filename.replace(".pdf", ".docx")
            cv = Converter(filename)
            cv.convert(output)
            cv.close()
            os.remove(filename)
            return send_file(output, as_attachment=True)

        elif option == 'image2word':
            reader = easyocr.Reader(['en'], gpu=False)
            result = reader.readtext(filename, detail=0)
            text = "\n".join(result)
            doc = Document()
            doc.add_paragraph(text)
            output = filename.rsplit('.', 1)[0] + "_ocr.docx"
            doc.save(output)
            os.remove(filename)
            return send_file(output, as_attachment=True)

        elif option == 'word2image':
            doc = Document(filename)
            text = "\n".join([p.text for p in doc.paragraphs])
            wrapped_text = "\n".join(textwrap.wrap(text, width=80))
            img = Image.new("RGB", (800, 1000), color="white")
            draw = ImageDraw.Draw(img)
            draw.text((20, 20), wrapped_text[:4000], fill="black")
            output = filename.replace(".docx", ".png")
            img.save(output)
            os.remove(filename)
            return send_file(output, as_attachment=True)

        elif option == 'image2pdf':
            img = Image.open(filename).convert('RGB')
            output = filename.rsplit('.', 1)[0] + ".pdf"
            img.save(output)
            os.remove(filename)
            return send_file(output, as_attachment=True)

        elif option == 'pdf2image':
            images = convert_from_path(filename)
            output_files = []
            for i, img in enumerate(images):
                out = f"{filename}_page{i+1}.png"
                img.save(out, 'PNG')
                output_files.append(out)

            zipname = filename.replace(".pdf", "_images.zip")
            with zipfile.ZipFile(zipname, 'w') as zipf:
                for f in output_files:
                    zipf.write(f)
                    os.remove(f)

            os.remove(filename)
            return send_file(zipname, as_attachment=True)

        return "Unsupported option", 400

    except Exception as e:
        return f"Internal Server Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
