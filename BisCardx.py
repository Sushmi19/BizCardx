import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import mysql.connector

# Image to text
def image_to_text(path):
    input_image = Image.open(path)
    image_arr = np.array(input_image)
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_arr, detail=0)
    return text, input_image

# Extract text from OCR output
def extract_text(texts):
    extract_dict = {"Name": [], "Designation": [], "Company Name": [], "Contact": [], "Email": [], "Web Site": [],
                    "Address": [], "Pincode": []}

    extract_dict["Name"].append(texts[0])
    extract_dict["Designation"].append(texts[1])

    for i in range(2, len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-", "").isdigit() and '-' in texts[i]):
            extract_dict["Contact"].append(texts[i])
        elif "@" in texts[i] and ".com" in texts[i]:
            extract_dict["Email"].append(texts[i])
        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
            small = texts[i].lower()
            extract_dict["Web Site"].append(small)
        elif "TamilNadu" in texts[i] or "Tami lNadu" in texts[i] or texts[i].isdigit():
            extract_dict["Pincode"].append(texts[i])
        elif re.match(r'^[A-Za-z]', texts[i]):
            extract_dict["Company Name"].append(texts[i])
        else:
            remove_colon = re.sub(r'[,;]', '', texts[i])
            extract_dict["Address"].append(remove_colon)

    for key, value in extract_dict.items():
        if len(value) > 0:
            concatenate = " ".join(value)
            extract_dict[key] = [concatenate]
        else:
            value = "NA"
            extract_dict[key] = [value]

    return extract_dict

# Streamlit Part
st.set_page_config(layout="wide")
st.markdown("<h1 style='font-family: Arial, sans-serif;'>Extracted Business Card Data With 'OCR'</h1>", unsafe_allow_html=True)

# SETTING-UP BACKGROUND IMAGE
def setting_bg():
    st.markdown(f""" <style>.stApp {{
                        background:url("https://wallpapers.com/images/featured/plain-zoom-background-d3zz0xne0jlqiepg.jpg");
                        background-size: cover}}
                     </style>""", unsafe_allow_html=True)


setting_bg()

# CREATING OPTION MENU
select = option_menu(None, ["Home", "Upload & Modify", "Delete"],
                       icons=["house", "cloud-upload", "pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "35px", "text-align": "centre", "margin": "-3px",
                                            "--hover-color": "#FFE5B4"},
                               "icon": {"font-size": "35px"},
                               "container": {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#71D9E2"}})

if select == "Home":
    # st.markdown("## :red[**Technologies Used :**] Python, easy OCR, Streamlit, SQL, Pandas")
    # st.markdown(
    #     "## :blue[**Overview :**] In this streamlit web app you can upload an image of a business card and extract "
    #     "relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. "
    #     "This app would also allow users to save the extracted information into a database along with the uploaded "
    #     "business card image. The database would be able to store multiple entries, each with its own business card "
    #     "image and extracted information."
    # )

    col1, col2 = st.columns(2)
    with col1:
        st.image(Image.open("C:\\Users\\User\\Desktop\\hello-colorful.gif"), width=500)
        st.markdown("## :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
    with col2:
        st.write(
            "## :red[**About :**] Bizcard is a Python application designed to extract information from business cards.")
        st.markdown(
            "## :blue[**Overview :**] In this streamlit web app you can upload an image of a business card and extract "
            "relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. "
            "This app would also allow users to save the extracted information into a database along with the uploaded "
            "business card image. The database would be able to store multiple entries, each with its own business card "
            "image and extracted information."
        )

elif select == "Upload & Modify":
    image = st.file_uploader("Please Upload the File", type=["png", "jpg", "jpeg"])

    if image is not None:
        st.image(image, width=300)
        Text_image, input_image = image_to_text(image)
        text_dict = extract_text(Text_image)

        if text_dict:
            st.success("Data is Extracted")

        tdf = pd.DataFrame(text_dict)
        img_bytes = io.BytesIO()
        input_image.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        data = {"Image": [img_data]}
        bdf = pd.DataFrame(data)
        con_df = pd.concat([tdf, bdf], axis=1)
        st.dataframe(con_df)

        button1 = st.button("Save")
        if button1:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mysql",
                auth_plugin='mysql_native_password',
                database="bizcardx_db"
            )

            cursor = mydb.cursor()

            table_query = '''CREATE TABLE IF NOT EXISTS bizcard_details (
                                name VARCHAR(255),
                                Designation VARCHAR(255),
                                Company_Name VARCHAR(255),
                                Contact VARCHAR(255),
                                Email VARCHAR(255),
                                Web_Site TEXT,
                                Address TEXT,
                                Pincode VARCHAR(255),
                                image LONGBLOB )'''

            cursor.execute(table_query)

            insert_query = '''INSERT INTO bizcard_details(name, Designation, Company_Name, Contact, Email, Web_Site, Address, Pincode, image)
                              VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'''

            datas = con_df.values.tolist()[0]
            cursor.execute(insert_query, datas)
            mydb.commit()

            st.success("Data Uploaded Successfully")

    method = st.radio("Select the method", ["none", "Show", "modify"])

    if method == "Show":
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            auth_plugin='mysql_native_password',
            database="bizcardx_db"
        )

        cursor = mydb.cursor()
        cursor.execute("USE bizcardx_db")
        select_query = "SELECT * FROM bizcard_details"

        cursor.execute(select_query)
        table = cursor.fetchall()

        table_df = pd.DataFrame(table, columns=("name", "Designation", "Company_Name", "Contact", "Email", "Web_Site",
                                                 "Address", "Pincode", "image"))
        st.dataframe(table_df)

    elif method == "modify":
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            auth_plugin='mysql_native_password',
            database="bizcardx_db"
        )

        cursor = mydb.cursor()
        cursor.execute("USE bizcardx_db")
        select_query = "SELECT * FROM bizcard_details"

        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()

        table_df = pd.DataFrame(table, columns=("name", "Designation", "Company_Name", "Contact", "Email", "Web_Site",
                                                 "Address", "Pincode", "image"))

        col1, col2 = st.columns(2)
        with col1:
            if not table_df.empty:
                select_name = st.selectbox("Select the name from list", table_df["name"])
        df_3 = table_df[table_df["name"] == select_name]

        df_4 = df_3.copy()

        col1, col2 = st.columns(2)
        with col1:
            if not df_3.empty:
                M_name = st.text_input("name", df_3["name"].iloc[0]) #.iloc[] is a method used to access rows and columns in a DataFrame by integer index position. It stands for "integer location"
                M_Desig = st.text_input("Designation", df_3["Designation"].iloc[0])
                M_cname = st.text_input("Company_Name", df_3["Company_Name"].iloc[0])
                M_cnt = st.text_input("Contact", df_3["Contact"].iloc[0])
                M_mail = st.text_input("Email", df_3["Email"].iloc[0])

                df_4["name"] = M_name
                df_4["Designation"] = M_Desig
                df_4["Company_Name"] = M_cname
                df_4["Contact"] = M_cnt
                df_4["Email"] = M_mail

        with col2:
            if not df_3.empty:
                M_Web = st.text_input("Web_Site", df_3["Web_Site"].iloc[0])
                M_add = st.text_input("Address", df_3["Address"].iloc[0])
                M_code = st.text_input("Pincode", df_3["Pincode"].iloc[0])
                M_img = st.text_input("image", df_3["image"].iloc[0])

                df_4["Web_Site"] = M_Web
                df_4["Address"] = M_add
                df_4["Pincode"] = M_code
                df_4["image"] = M_img

        st.dataframe(df_4)

        col1, col2 = st.columns(2)
        with col1:
            b1 = st.button("Alter", use_container_width=True)

        if b1 and not df_3.empty:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mysql",
                auth_plugin='mysql_native_password',
                database="bizcardx_db"
            )

            cursor = mydb.cursor()
            cursor.execute("USE bizcardx_db")
            cursor.execute(f" DELETE FROM bizcard_details WHERE NAME='{select_name}'")
            mydb.commit()

            insert_query = '''INSERT INTO bizcard_details(name, Designation, Company_Name, Contact, Email, Web_Site, 
                                                            Address, Pincode,image) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'''

            datas = df_4.values.tolist()[0]
            cursor.execute(insert_query, datas)
            mydb.commit()

            st.success("Altered Successfully")

elif select == "Delete":
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql",
        auth_plugin='mysql_native_password',
        database="bizcardx_db"
    )

    cursor = mydb.cursor()
    cursor.execute("USE bizcardx_db")

    # Delete section
    select_query = "SELECT name FROM bizcard_details"
    cursor.execute(select_query)
    table_1 = cursor.fetchall()
    names = [i[0] for i in table_1]
    select_name = st.selectbox("Select the Name", names)

    select_query = f"SELECT Designation FROM bizcard_details WHERE name= '{select_name}'"
    cursor.execute(select_query)
    table_2 = cursor.fetchall()
    designation = [j[0] for j in table_2]
    select_designation = st.selectbox("Select the Designation", designation)

    if select_name and select_designation:
        st.write(f" Selected Name: {select_name}")
        st.write("")
        st.write("")
        st.write("")
        st.write(f"Selected Designation: {select_designation}")

    remove = st.button("Delete", use_container_width=True)

    if remove:
        cursor.execute(f"DELETE FROM bizcard_details WHERE name='{select_name}' AND Designation ='{select_designation}' ")
        mydb.commit()
        st.warning("Deleted")
