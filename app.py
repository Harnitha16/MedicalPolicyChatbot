# Day 3 
# lets create folders , api key and test it.

#create folder for files

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma



dir_name = 'resources'

if not os.path.exists(dir_name):
    os.makedirs(dir_name)

load_dotenv()

# lets test the api

model = ChatOpenAI(model = 'gpt-3.5-turbo')

# while True:
#     prompt = input("Hey LLM:")
#     if prompt.lower() == 'bye':
#         break

#     response = model.invoke(prompt)
#     print("Answer:", response.content)


#DAY4

file_path = 'resources/StarHealthAssureInsurancePolicy-Policy.pdf'
loader = PyMuPDFLoader(file_path)
document = loader.load()

# print(document)

# lets chunk

text_splitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap=200)
doc = text_splitter.split_documents(document)

# print("Number of chunks:",len(doc))

# print(doc[0])

#DAY 5 -Emedding and Vector Store Creation

embedding = OpenAIEmbeddings(model = 'text-embedding-3-small')

persistant_directory = 'db'

if not os.path.exists(persistant_directory):
    os.makedirs(persistant_directory)

persistant_folder = os.path.join(persistant_directory,'chroma_star_ins')



db = Chroma.from_documents(
    doc,
    embedding,
    persist_directory = persistant_folder
)

# print(db)

#DAY 6 - Retrive revelant documents

retriever = db.as_retriever(
    search_type = 'similarity_score_threshold',
    search_kwargs = {'k':5,'score_threshold':0.2}
)

query ='What is the policy about?'

relevant_docs = retriever.invoke(query)

for i,doc in enumerate(relevant_docs):
    print(f'Doc{i}')

res = model.invoke(f'{query}Answer using{relevant_docs}')
print(res.content)