
import streamlit as st
import pandas as pd
from pandasai.llm import HuggingFaceTextGen
from pandasai import SmartDataframe
from pandasai.connectors import PandasConnector

# Load and cache the dataframe
@st.cache_data
def load_csv():
    # Load the CSV file from the current directory
    df = pd.read_csv('claim_data.csv')

    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    
    df['TM Invoice Date'] = df['TM Invoice Date'].str.strip()
    df['Retail invoice Date'] = df['Retail invoice Date'].str.strip()
    df['SAP Doc Date'] = df['SAP Doc Date'].str.strip()

    df['TM Invoice Date'] = pd.to_datetime(df['TM Invoice Date'], errors='coerce', infer_datetime_format=True)
    df['Retail invoice Date'] = pd.to_datetime(df['Retail invoice Date'], errors='coerce', infer_datetime_format=True)
    df['SAP Doc Date'] = pd.to_datetime(df['SAP Doc Date'], errors='coerce', infer_datetime_format=True)

    df['TMInvoiceno'] = df['TMInvoiceno'].astype(str)
    df['Dealer Code'] = df['Dealer Code'].astype(str)
    df['G_Claim ID'] = df['G_Claim ID'].astype(str)

    nat_rows = df[df['TM Invoice Date'].isna() | df['Retail invoice Date'].isna() | df['SAP Doc Date'].isna()]
    st.write("Rows with missing dates:", nat_rows[['TM Invoice Date', 'Retail invoice Date', 'SAP Doc Date']])

    return df

# Load and initialize the dataframe and SmartDataframe
@st.cache_resource
def initialize_smart_df(df):
    llm = HuggingFaceTextGen(
        inference_server_url="http://127.0.0.1:8080"  # Replace with your actual inference server URL
    )
    
    

    field_info = {
    'Dealer Code': 'The unique identifier for each dealer.',
    'Dealer Name': 'The name of the dealer associated with the claim.',
    'Dealer State': 'The state in which the dealer is located.',
    'Region': 'The geographical region of the dealer.',
    'Status': 'The current status of the claim (e.g., Settled, Pending).',
    'Status Reson': 'The reason for the current status of the claim.',
    'Chassis no': 'The unique chassis number of the vehicle associated with the claim.',
    'TMInvoiceno': 'The invoice number issued by the TM (Tata Motors) for the claim.',
    'TM Invoice Date': 'The date on which the TM invoice was issued.',
    'Retail invoice no': 'The invoice number issued by the retailer.',
    'Retail invoice Date': 'The date on which the retail invoice was issued.',
    'Claim ID': 'The unique identifier for the claim.',
    'G_Claim ID': 'The identifier for the group claim, if applicable.',
    'Scheme ID': 'The identifier for the scheme under which the claim is made.',
    'Amount': 'The monetary amount claimed.',
    'SAP Doc no.': 'The document number generated by SAP for the claim.',
    'SAP Doc Date': 'The date on which the SAP document was generated.',
    'Scheme Type': 'The type of scheme under which the claim is made.',
    'Scheme Type-Name': 'The name of the scheme under which the claim is made.',
    'Scheme Type Category': 'The category of the scheme under which the claim is made.',
    'LOB': 'The line of business (LOB) associated with the claim.'
                    } 

    connector = PandasConnector({"original_df": df}, field_descriptions=field_info)
    sdf = SmartDataframe(connector,config={'llm':llm})

    
    return sdf, field_info

df = load_csv()

# Initialize SmartDataframe
sdf, field_info = initialize_smart_df(df)

# Streamlit app UI
st.title("CSV Chatbot")
st.write("Ask questions about the data in the CSV file.")



# Text input for the user's question
question = st.text_input("Your Question:")

if st.button("Ask"):
    if question:
        try:
            # Get the answer from the SmartDataframe
            answer = sdf.chat(question)
            st.write("Answer:", answer)
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a question.")
