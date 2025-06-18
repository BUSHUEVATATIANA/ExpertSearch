from pymilvus import connections, MilvusClient, DataType, model
import pandas as pd
from datetime import date
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import emoji
import re
from scripts.prerocess_text import preprocess_text

connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)
client = MilvusClient(uri="http://localhost:19530", token=token)

model_sf = SentenceTransformer("intfloat/multilingual-e5-large-instruct")

def create_batches(df, batch_size):
    return [df.iloc[i:i + batch_size] for i in range(0, len(df), batch_size)]

def load_to_milvus(data):
    data['description'] = data['description'].apply(lambda x: preprocess_text(x))
    today = date.today()
    data['date'] = str(today)
    batches = create_batches(data, 32)
    for batch in tqdm(batches):
        text = batch['description'].apply(lambda x: preprocess_text(x))
        embeddings = text.apply(lambda x: model_sf.encode(x, normalize_embeddings=True))
        #embeddings = model_sf.encode(text, normalize_embeddings=True)
        data1 = [
            {"my_id": index, "num": num, "description_embedding": embedding, "description": description, "filter_rate": filter_rate,
            'sum_rate_on_site': sum_rate_on_site, 'review': review,'fake_rating': fake_rating,'date': date, 'contact_details': contact_details, 'name': name, 'location': location}
            for index, num, embedding, description, filter_rate, sum_rate_on_site, review, fake_rating, date, contact_details, name, location in zip(
                batch['index'],batch["num"], embeddings, batch["description"], batch["rate"], batch['sum_review'], batch['review'], batch['fake_rating'], batch['date'], batch['contact_details'], batch['name'], batch['location']
            )
        ]
        res = client.upsert(collection_name= 'experts_z', data=data1)
