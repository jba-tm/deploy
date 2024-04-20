import openai
import pinecone
from app.conf.config import settings
from .exceptions import PineconeUploadException


def upload(text_list, pinecone_name: str, api_key: str, environment: str):
    try:
        pinecone.init(api_key=api_key, environment=environment)
        index = pinecone.Index(pinecone_name)

        # Set OpenAI API key and model
        if not settings.OPENAI_API_KEY:
            raise Exception("Invalid OPENAI_API_KEY key")
        openai.api_key = settings.OPENAI_API_KEY
        model = "text-embedding-ada-002"

        batch_size = 32  # Process everything in batches of 32
        for i in range(0, len(text_list), batch_size):
            # Set end position of batch
            i_end = min(i+batch_size, len(text_list))
            # Get batch of lines and IDs
            lines_batch = text_list[i: i+batch_size]
            ids_batch = [str(n) for n in range(i, i_end)]
            # Create embeddings
            res = openai.Embedding.create(input=lines_batch, engine=model)
            embeds = [record['embedding'] for record in res['data']]
            # Prepare metadata and upsert batch
            meta = [{'text': line} for line in lines_batch]
            to_upsert = zip(ids_batch, embeds, meta)
            # Upsert to Pinecone
            index.upsert(vectors=list(to_upsert))
    except Exception as e:
        # Handle exceptions appropriately
        raise PineconeUploadException(e)
