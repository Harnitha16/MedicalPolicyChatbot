import os
from langchain_openai import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import streamlit as st
import PyPDF2
import shutil


import streamlit as st

st.title('KnowYourPolicy')

# embedding = OpenAIEmbeddings(model='text-embedding-3-small')
# model = ChatOpenAI(model = 'gpt-3.5-turbo')
persistant_directory = 'db'

if not os.path.exists(persistant_directory):
     os.makedirs(persistant_directory)

about ="""
    This application helps you understand your insurance policy documents. Upload a PDF, and once it’s processed, you can ask questions about its contents.
"""

api_key = st.text_input('Enter your OpenAI API key:',type='password')
try:
    if api_key:
        embedding = OpenAIEmbeddings(model='text-embedding-3-small', api_key=api_key)
        model = ChatOpenAI(model = 'gpt-3.5-turbo', api_key=api_key)
        check = model.invoke('Greet with a friendly note.')
        st.success('OpenAI API Auth successful')
        st.info(check.content)
        st.info(about)
    else:
        st.info('Enter OpenAI API to proceed.')
        st.info("If you dont have a API Key, check out this [Youtube](https://youtu.be/05izydnrnZ4?si=u2tGXGprWsgWs3Ju) to get one. ")

except Exception as e:
    st.error('Check API key.')


# File uploader
uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
documents=''

if uploaded_files and api_key:
    st.write(f"Uploaded {len(uploaded_files)} file(s):")
    
    for i,uploaded_file in enumerate(uploaded_files):
        st.write(f"📄 {uploaded_file.name}")
        
        # Example: show file size
        st.write(f"Size: {uploaded_file.size / 1024:.2f} KB")
        
        # Optional: Read content with PyPDF2
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            documents += text
            st.success(f"Uploaded {uploaded_file.name}")
            st.success(f'{documents[:100]}.....')
        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {e}")

   
    text_splitter = CharacterTextSplitter(separator=" ",chunk_size = 1000, chunk_overlap=200)
    document_chucked = text_splitter.split_text(documents)
        

    persistant_folder = os.path.join(persistant_directory,f'chroma_db')
    if not os.path.exists(persistant_folder):
        os.makedirs(persistant_folder)

    db = Chroma.from_texts(
            document_chucked,
            embedding,
            persist_directory = persistant_folder
        )


    retriever = db.as_retriever(
            search_type = 'mmr',
            search_kwargs = {'k':10,'lambda_mult':0.5}
        )

    query = st.text_input('Query:',placeholder='\'Ask your question here\' and press Enter')

    instruction = """You are an expert policy advisor. Given a policy document 
                        answer the Query in a detailed and specific manner.
                        Do not answer away from the information provided. 
                        Say to please repharse the question, if you do not know the answer.
                        Do not provide false answer.Do not speculate.
                        Follow the below format.
                        Answer in butteins
                        'Source:' Give the extract sentence without changing any word from the information given through which you answered.
                        The query and information is as follows:
                        """

    if query:

            relevant_docs = retriever.invoke(query)
            res = model.invoke(f'{instruction} Query:{query}Answer using this information:{relevant_docs}')
            st.write('Response')
            st.info(f'{res.content}')

del_button = st.button('End Session')
if del_button:
    st.markdown(
    '<meta http-equiv="refresh" content="0; URL=./">',
    unsafe_allow_html=True
    )
    if os.path.exists(persistant_folder):
        shutil.rmtree(persistant_folder)
