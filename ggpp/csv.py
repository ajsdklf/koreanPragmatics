import streamlit as st 

def load_csv(file_path):
    """
    Load a CSV file from the given file path.
    
    :param file_path: Path to the CSV file
    :return: DataFrame containing the CSV data
    """
    return pd.read_csv(file_path)


