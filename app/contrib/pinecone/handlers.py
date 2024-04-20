import os
import re
import gzip
import zipfile
import shutil
from typing import Optional
from pdfminer.high_level import extract_text
from loguru import logger
import xlrd
from langchain.text_splitter import CharacterTextSplitter
from .exceptions import SplitterException, PineconeFileHandlerException
from .upload import upload as pinecone_upload


def read_raw_text_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()
        if file_path.endswith('.xml'):
            raw_text = re.sub('</\w*>', '', raw_text)
            raw_text = re.sub('<', '', raw_text)
            raw_text = re.sub('>', ':', raw_text)
        return raw_text


def extract_text_from_file(
        file_path,
        pinecone_name: str, api_key: str, environment: str,
        separator=",",
        chunk_size=1000,
        chunk_overlap=200
):
    try:
        extension = os.path.splitext(file_path)[-1]
        raw_text = ""
        if extension == '.pdf':
            raw_text = extract_text(file_path)
        elif extension in [".xls", ".xlsx"]:
            book = xlrd.open_workbook(file_path)
            for sheet in book.sheets():
                for row in range(sheet.nrows):
                    raw_text += ','.join(map(str, sheet.row_values(row))) + '\n'
        elif extension in [".json", ".csv", ".xml"]:
            raw_text = read_raw_text_file(file_path)
        if raw_text:
            textsplitter = CharacterTextSplitter(
                separator=separator,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len
            )
            texts = textsplitter.split_text(raw_text)
            pinecone_upload(texts, pinecone_name=pinecone_name, environment=environment, api_key=api_key)
        return raw_text
    except Exception as e:
        logger.error(str(e))
        # raise SplitterException(e)


def dir_handler(
        directory, pinecone_name: str, api_key: str, environment: str, remove: Optional[bool] = False
):
    try:
        for root, dirs, files in os.walk(directory):
            # print(dirs, files)
            for file in files:
                file_path = os.path.join(root, file)
                file_handler(file_path, pinecone_name=pinecone_name, environment=environment, api_key=api_key)
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                dir_handler(dir_path, pinecone_name=pinecone_name, environment=environment, api_key=api_key)
        if remove:
            shutil.rmtree(directory)
    except Exception as e:
        print(e)
        logger.error(str(e))


def zip_file_handler(filename, pinecone_name: str, api_key: str, environment: str):
    try:
        extract_dir, extension = os.path.splitext(filename)
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(file=filename, mode='r') as f:
            f.extractall(extract_dir)
        dir_handler(extract_dir, pinecone_name=pinecone_name, environment=environment, api_key=api_key)
    except Exception as e:
        logger.error(str(e))


def gz_file_handler(
        filename, pinecone_name: str, api_key: str, environment: str,
        separator=",",
        chunk_size=1000,
        chunk_overlap=200
):
    try:
        suffix = os.path.splitext(filename)[0]
        suffix = os.path.splitext(suffix)[-1]
        raw_text = ""
        with gzip.GzipFile(filename=filename, mode='r') as f:
            raw_text = f.read()
            if suffix == ".xml":
                raw_text = re.sub('</\w*>', '', raw_text)
                raw_text = re.sub('<', '', raw_text)
                raw_text = re.sub('>', ':', raw_text)

        if raw_text:
            textsplitter = CharacterTextSplitter(
                separator=separator,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len
            )
            texts = textsplitter.split_text(raw_text)
            pinecone_upload(texts, pinecone_name=pinecone_name, environment=environment, api_key=api_key)

    except Exception as e:
        logger.error(str(e))


def file_handler(file_path, pinecone_name: str, api_key: str, environment: str):
    try:
        extension = os.path.splitext(file_path)[-1]
        if extension == ".zip":
            zip_file_handler(file_path, pinecone_name=pinecone_name, environment=environment, api_key=api_key)
            return
        elif extension == ".gz":
            gz_file_handler(file_path, pinecone_name=pinecone_name, environment=environment, api_key=api_key)
            return
        else:
            extract_text_from_file(file_path, pinecone_name=pinecone_name, environment=environment, api_key=api_key)
    except Exception as e:
        logger.error(str(e))

        # raise PineconeFileHandlerException(e)
