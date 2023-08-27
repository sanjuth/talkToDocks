from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders.csv_loader import CSVLoader
import nbformat
from nbconvert import PythonExporter


def split_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                               chunk_overlap=15,
                                               length_function=len)
    doc_list = []
    for pg in pages:
        pg_splits = textSplit.split_text(pg.page_content)
        doc_list.extend(pg_splits)

    return doc_list


def get_text_splits(text_file):
    with open(text_file, 'r') as txt:
        data = txt.read()

    textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                               chunk_overlap=15,
                                               length_function=len)
    doc_list = textSplit.split_text(data)
    return doc_list


def get_csv_splits(csv_file):
    csvLoader = CSVLoader(csv_file)
    csvdocs = csvLoader.load()
    return csvdocs


def get_ipynb_splits(notebook):
    with open(notebook) as fh:
        nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)
    exporter = PythonExporter()
    source, meta = exporter.from_notebook_node(nb)
    textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                               chunk_overlap=15,
                                               length_function=len)
    doc_list = textSplit.split_text(source)
    return doc_list

# need to work on git splitting

# def get_git_files(repo_link, folder_path, file_ext):
#   git_loader = GitLoader(clone_url=repo_link,
#     repo_path=folder_path,
#     file_filter=lambda file_path: file_path.endswith(file_ext))
#   git_docs = git_loader.load()
#   textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
#                                              chunk_overlap=15,
#                                              length_function=len)
#   doc_list = []
#   for code in git_docs:
#     code_splits = textSplit.split_text(code.page_content)
#     doc_list.extend(code_splits)
#   return doc_list


def file_split(file_path, filename):
    file_type = filename[-3:]
    if file_type == 'pdf':
        return split_pdf(file_path)
    elif file_type == 'txt':
        return get_text_splits(file_path)
    elif file_type == 'csv':
        return get_csv_splits(file_path)
    elif filename[-5:] == 'ipynb':
        return get_ipynb_splits(file_path)
