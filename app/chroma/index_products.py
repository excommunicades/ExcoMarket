import os
from dotenv import load_dotenv
from chromadb import HttpClient

from db.models import Product
from main import app
from db.extensions import db

load_dotenv()

chromadb_host = os.getenv("CHROMADB_HOST", "chroma")
client = HttpClient(host=chromadb_host, port=8000)
collection = client.get_or_create_collection(name="products")


def get_all_products():
    with app.app_context():
        return Product.query.all()


def index_products():
    """
    Retrieve all products, prepare documents and metadata,
    and add them to the 'products' ChromaDB collection.
    """
    products = get_all_products()
    documents, ids, metadatas = [], [], []

    for product in products:
        doc = f"{product.name}. {product.description}"
        doc_id = str(product.id)

        price = (
            float(product.price)
            if product.price is not None and isinstance(product.price, (int, float))
            else 0.0
        )
        metadata = {
            "name": product.name,
            "description": product.description,
            "price": price
        }

        documents.append(doc)
        ids.append(doc_id)
        metadatas.append(metadata)

    if not documents or not ids or not metadatas:
        print("⚠️ No products found to index. Skipping ChromaDB add.")
        return

    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )

    print(f"\n✅ Indexed {len(documents)} products in the collection 'products'.")
