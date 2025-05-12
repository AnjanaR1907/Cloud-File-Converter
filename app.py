from flask import Flask, request, send_file, render_template_string
import pytesseract
from PIL import Image
from pdf2docx import Converter
import os

app = Flask(__name__)

# HTML as string (since no templates folder)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Cloud File Converter</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      margin-top: 50px;
    }
    form {
      background: #f2f2f2;
      padding: 20px;
      display: inline-block;
      border-radius: 10px;
    }
  </style>
</head>
<body>
  <h1>Cloud File Converter</h1>
  <form action="/convert" method="POST" enctype="multipart/form-data">
    <label>Select File:</label><br>
    <input type="file" name="file" required><br><br>

    <label>Conversion Type:</label><br>
    <select name="option">
      <option value="image2text">Image to Text</option>
      <option value="pdf2docx">PDF to Word</option>
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
    file = request.files['file']
    option = request.form['option']
    filename = file.filename
    file.save(filename)

    if option == 'image2text':
        text = pytesseract.image_to_string(Image.open(filename))
        output_path = "output.txt"
        with open(output_path, "w") as f:
            f.write(text)
        os.remove(filename)
        return send_file(output_path, as_attachment=True)

    elif option == 'pdf2docx':
        output_path = "converted.docx"
        cv = Converter(filename)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        os.remove(filename)
        return send_file(output_path, as_attachment=True)

    return "Unsupported operation", 400

if __name__ == '__main__':
    app.run(debug=True)
