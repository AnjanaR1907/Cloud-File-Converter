from flask import Flask, request, render_template, send_file
import pytesseract
from PIL import Image
from pdf2docx import Converter
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
