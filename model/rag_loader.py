import os
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.readers.github import GithubRepositoryReader, GithubClient
from google.oauth2 import service_account  # 認証用

from config import settings

def initialize_llama_index_settings():
    """Llama Indexの設定を初期化"""
    if settings.USE_VERTEX_AI:
        # === Vertex AIモード ===
        from llama_index.llms.vertex import Vertex
        from llama_index.embeddings.vertex import VertexTextEmbedding

        print("🔧 Llama Index: Vertex AIモードの設定を初期化中...")

        # 認証情報を明示的にロード
        json_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        credentials = None
        if json_path and os.path.exists(json_path):
            credentials = service_account.Credentials.from_service_account_file(json_path)

        # Embeddingモデルの設定
        Settings.embed_model = VertexTextEmbedding(
            model_name="text-embedding-004",
            project=settings.GCP_PROJECT_ID,
            location=settings.GCP_LOCATION,
            credentials=credentials
        )

        # LLMの設定
        Settings.llm = Vertex(
            model=settings.GEMINI_PRO_MODEL_NAME,
            project=settings.GCP_PROJECT_ID,
            location=settings.GCP_LOCATION,
            credentials=credentials,
            max_tokens=4096,        # 出力トークン数（回答の長さ）
            temperature=0.1,        # ランダム性（低め推奨）
            context_window=1000000  # コンテキストウィンドウ（モデルの入力容量）を明示
        )

        print("✅ Llama Index: Vertex AIモードの設定が完了しました。")
    
    else:
        # === AI Studioモード ===
        from llama_index.llms.gemini import Gemini
        from llama_index.embeddings.gemini import GeminiEmbedding

        print("🔧 Llama Index: Gemini APIモードの設定を初期化中...")
        
        # APIキーの設定
        os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY

        Settings.embed_model = GeminiEmbedding(
            model_name="models/text-embedding-004"
        )

        Settings.llm = Gemini(
            model=settings.GEMINI_PRO_MODEL_NAME,
            max_tokens=4096,
            temperature=0.1,
            context_window=1000000
        )

        print("✅ Llama Index: Gemini APIモードの設定が完了しました。")
    

def get_index():
    """
    ChromaDBからインデックスをロード，なければGithubリポジトリからデータを取得してインデックスを作成し保存
    """

    # Llama Indexの設定を初期化
    initialize_llama_index_settings()

    # ChromaDBのクライアントの設定（永続化設定）
    db_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    chroma_collection = db_client.get_or_create_collection(name=settings.CHROMA_COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # データが存在するか確認
    if chroma_collection.count() > 0:
        print("📂 既存のインデックスをChromaDBからロード中...")
        
        # 修正: ベクトルストアからのロードは load_from_storage ではなく from_vector_store
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context
        )
        print("✅ インデックスのロードが完了しました。")
        return index

    else:
        print("🚀 既存のインデックスが見つからないため，Githubリポジトリからデータを取得して新規インデックスを作成します...")

        # Githubリポジトリクライアントの初期化
        github_client = GithubClient(
            github_token=settings.GITHUB_TOKEN,
            verbose=True
        )

        # リポジトリリーダーの初期化
        repo_reader = GithubRepositoryReader(
            github_client=github_client,
            owner=settings.GITHUB_REPO_OWNER,
            repo=settings.GITHUB_REPO_NAME,
            filter_file_extensions=(
                [".py", ".js", ".ts", ".md", ".html", ".css", ".json", ".yaml", ".yml", ".sql", ".go", ".java", ".txt"],
                GithubRepositoryReader.FilterType.INCLUDE
            ),
            verbose=True,
            concurrent_requests=5
        )

        # ドキュメントの取得
        print(f"📥 ブランチ '{settings.GITHUB_BRANCH_NAME}' からデータを取得中...")
        documents = repo_reader.load_data(branch=settings.GITHUB_BRANCH_NAME)
        print(f"📄 {len(documents)} 件のドキュメントを取得しました")

        # インデックス作成と同時に保存
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context
        )
        print("✅ インデックスの作成と保存が完了しました。")
        return index