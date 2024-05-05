# BizCardX - Extracting Business Card Data with OCR

# OCr
OCR or Optical Character Recognition is also referred to as text recognition or text extraction. This machine learning-based easyOCR technique allows users to extract printed or handwritten text from posters, cards, documents, etc. The text can be words, text lines or paragraphs enabling us to have a digital version of scanned text. This significantly eliminates manual entry. The OCR used here is by JAIDED AI.

# Tools Install
* Python 3.x (https://www.python.org/downloads/)
* Streamlit (pip install streamlit)
* Streamlit option menu (pip install streamlit-option-menu)
* Mysql.connector ( Pip install mysql.connector)
* Pandas (pip install pandas)

# Text Detection
Using easyOCR all the text in the card is detected using the business card image.
```
reader = easyocr.Reader(['en'])
text = reader.readtext(image_arr, detail=0)
```
The detections are viewed by drawing a bounding box around the text with the text coordinates from the results.

# Text Recognition
The card details are recognized as a specific field using regular expression Python and stored in a pandas data frame.

# Streamlit Dashboard
The detected card details are stored in SQL DB for viewing, modifying, and deleting a stored card by the user.
These functionalities are provided to the user with button input elements by streamlit.
The web application is deployed for use by others.


    

