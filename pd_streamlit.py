import streamlit as st


##############Core functionality###################

import argparse
import pandas as pd
from pandasai.llm import HuggingFaceTextGen
from pandasai import SmartDataframe
from pandasai.connectors import PandasConnector

def load_csv_and_initialize_smart_df():
    llm = HuggingFaceTextGen(
        inference_server_url="http://127.0.0.1:8080"  # Replace with your actual inference server URL
    )
    
    # Load the CSV file from the current directory
    df = pd.read_csv('claim_data.csv')

    print(df.head())

    if 'Unnamed: 0' in df.columns:
    # Drop the column if it exists
        df = df.drop(columns=['Unnamed: 0'])
    
    # Convert date columns to datetime format

    df['TM Invoice Date'] = df['TM Invoice Date'].str.strip()
    df['Retail invoice Date'] = df['Retail invoice Date'].str.strip()
    df['SAP Doc Date'] = df['SAP Doc Date'].str.strip()

    df['TM Invoice Date'] = pd.to_datetime(df['TM Invoice Date'], errors='coerce', infer_datetime_format=True)
    df['Retail invoice Date'] = pd.to_datetime(df['Retail invoice Date'], errors='coerce', infer_datetime_format=True)
    df['SAP Doc Date'] = pd.to_datetime(df['SAP Doc Date'], errors='coerce', infer_datetime_format=True)
    
    # Convert string columns
    df['TMInvoiceno'] = df['TMInvoiceno'].astype(str)
    df['Dealer Code'] = df['Dealer Code'].astype(str)
    df['G_Claim ID'] = df['G_Claim ID'].astype(str)
    print(df.info())
    print(df.head())

    nat_rows = df[df['TM Invoice Date'].isna() | df['Retail invoice Date'].isna() | df['SAP Doc Date'].isna()]
    print(nat_rows[['TM Invoice Date', 'Retail invoice Date', 'SAP Doc Date']])
    
    # Define the field_info dictionary
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
    
    # Initialize SmartDataframe with the field_info
    connector = PandasConnector({"original_df": df}, field_descriptions=field_info)
    sdf = SmartDataframe(connector,config={'llm':llm})
    
    return sdf

def ask_question(sdf, query):
    response = sdf.chat(query)
    return response

sdf = load_csv_and_initialize_smart_df()

# def main():
#     parser = argparse.ArgumentParser(description="Chat with a CSV using PandasAI SmartDataframe")
#     parser.add_argument("query", help="Your question to the CSV")
#     args = parser.parse_args()

#     sdf = load_csv_and_initialize_smart_df()
#     response = ask_question(sdf, args.query)
#     print(response)

# if __name__ == "__main__":
#     main()

#######################################################


st.title("TML chatBot")

st.session_state.messages = []

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How may i help you?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    
    response = ask_question(sdf, prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})