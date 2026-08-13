import os
import datetime
import chromadb
import uuid

class HermesLongTermMemory:
    def __init__(self, db_path="data/chroma_db"):
        print("[Memory Subsystem]: Initializing ChromaDB Long-Term Storage (Default Native Engine)...")
        
        # Create a persistent local database on your hard drive
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        
        try:
            # Use ChromaDB's native default embedding function (100% stable, offline, zero dependency conflicts)
            self.collection = self.client.get_or_create_collection(
                name="hermes_memories"
            )
            print("[Memory Subsystem]: Long-Term Storage Online and Ready (Native Embeddings Active).")
        except Exception as e:
            print(f"[Memory Error]: Failed to initialize collection - {e}")
            self.collection = None

    def remember(self, text: str, source: str = "conversation"):
        """
        Saves a piece of information permanently into the vector database.
        """
        if not self.collection or not text or len(text.strip()) < 5:
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Added a short UUID to prevent ID collisions if multiple memories save in the exact same second
        doc_id = f"mem_{timestamp.replace(' ', '_').replace(':', '')}_{str(uuid.uuid4())[:8]}"

        try:
            self.collection.add(
                documents=[text],
                metadatas=[{"source": source, "timestamp": timestamp}],
                ids=[doc_id]
            )
            # Suppressed the print statement here so the Brain's 'Passive Learning Triggered' log stays clean
        except Exception as e:
            print(f"[Memory Error]: Failed to store data - {e}")

    def recall(self, query: str, n_results: int = 3) -> str:
        """
        Searches the database for memories semantically related to the query.
        Returns them as a formatted string to inject into the LLM context.
        """
        if not self.collection:
            return ""

        try:
            # CRITICAL BUG FIX: ChromaDB will crash if you ask for 3 results but only have 1 or 2 saved.
            collection_size = self.collection.count()
            if collection_size == 0:
                return ""
            
            safe_n_results = min(n_results, collection_size)

            results = self.collection.query(
                query_texts=[query],
                n_results=safe_n_results
            )
            
            if not results['documents'] or not results['documents'][0]:
                return ""

            recalled_facts = []
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                recalled_facts.append(f"[{meta['timestamp']}] Past Knowledge: {doc}")

            return "\n".join(recalled_facts)
        except Exception as e:
            print(f"[Memory Error]: Failed to recall data - {e}")
            return ""