from sentence_transformers import SentenceTransformer

class Get_embeddings:
    def __init__(self):
        self.model = SentenceTransformer('/opt/airflow/dags/scripts/st_ft_epoch100')
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        train_embeddings  = list(model.encode(X))
        return train_embeddings