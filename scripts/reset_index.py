from app.config import get_settings
from app.core.vector_store import VectorStore


if __name__ == "__main__":
    store = VectorStore(get_settings())
    deleted = store.reset()
    print("İndeks silindi." if deleted else "Silinecek indeks bulunamadı.")
