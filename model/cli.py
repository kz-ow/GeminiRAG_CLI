from rag_loader import get_index

def main():
    print("🤖 RAG検証用 CLIツールを起動します...")
    
    try:
        # 1. インデックスの準備
        index = get_index()
        
        # 2. 検索エンジンの作成
        query_engine = index.as_query_engine(similarity_top_k=5)
        
        print("\n✅ 準備完了！質問を入力してください (終了するには 'exit' と入力)")
        print("-" * 50)

        while True:
            # ユーザー入力を受け取る
            user_input = input("\nUser > ")
            
            if user_input.lower() in ["exit", "quit", "終了"]:
                print("👋 終了します")
                break
            
            if not user_input.strip():
                continue

            print("🤖 Thinking...")
            
            # RAG実行
            response = query_engine.query(user_input)
            
            # 結果表示
            print(f"\nBot > {response}")
            
            # どのファイルを参考にしたかを表示（デバッグ用）
            print("\n🔍 参照ソース:")
            for node in response.source_nodes:
                print(f"- {node.metadata.get('file_path', 'unknown')} (Score: {node.score:.2f})")
            print("-" * 50)

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()