# GeminiRAG_CLI

LlamaIndex × Gemini で、**GitHubリポジトリの「コード」だけでなく「PR / Issue の議論」も含めて参照**できるRAG（Retrieval-Augmented Generation）を、CLI形式で手軽に実行できるツールです．以下が今回作成したGeminiRAG_CLIの主な特徴です．
- 「この関数は何のために入った？」（= **変更の意図**）まで追える
- **Google AI Studio / Vertex AI** を `USE_VERTEX_AI` 1つで切り替え可能
- ベクタDBは **ChromaDB** を利用（ローカル永続化）

## 1．デモ動画
以下が完成品のデモ動画です．デモ動画では，実際に自作した既存アプリケーションのリポジトリである Linebotリポジトリ を参照しながら，「verify_tokenというメソッドがどのような用途のために作成されたか」を質問してみました．

![ragデモ動画.gif](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3856953/e70d94a1-121a-4fad-8813-ff3d6d0b708f.gif)

## 2．技術スタック
以下が使用した技術スタックです．

| Category | Stack | Version / Model |
|---|---|---|
| LLM | Gemini | `gemini-2.5-pro`, `gemini-2.5-flash` |
| Embedding | text-embedding-004 | `text-embedding-004` |
| RAG Framework | LlamaIndex | `llama-index-core==0.14.8` |
| Vector DB | ChromaDB | `chromadb==1.3.5` |
| AI Platform (Dev) | Google AI Studio | `google-generativeai==0.8.5` |
| AI Platform (Prod) | Vertex AI | `google-cloud-aiplatform==1.128.0` |
| Runtime | Python | `3.12-slim` |
| Infra | Docker / Docker Compose | Compose file v3系 |

## 当リポジトリを使用する際の事前準備
### 必須
- Docker
- Docker Compose
- 参照対象リポジトリにアクセスできる **GitHub Token**
  - 参照するリポジトリがpublicである場合は不要です    

### 以下のいずれか
- **Google AI Studio** の Gemini API Key  
  または
- **Vertex AI** を使うための GCP プロジェクト / 認証（Service Account）
  - 入力データを学習データに使用されたくない場合はこちらの使用を推奨

---

## セットアップ

### 1) リポジトリをクローン
以下のコマンドを実行し，リポジトリをクローンしてください
```bash
git clone https://github.com/kz-ow/GeminiRAG_CLI.git
cd GeminiRAG_CLI

### 2) .envファイルの作成
以下のフォーマットの.envファイルを作成し，各種APIキーの値を設定してください．
※ AI Studio を使う場合は USE_VERTEX_AI=False にし，Google AI Studio関連の部分のみを埋めてください（GCP設定は不要です）

```shell:.env
# 各環境変数（APIキー）

# Google AI Studio関連
GEMINI_API_KEY=your_gemini_apikey
GEMINI_REGION=your_gemini_region

# GCP設定
GOOGLE_APPLICATION_CREDENTIALS=/model/service-account.json
GCP_PROJECT_ID=your_gcp_project_id
GCP_LOCATION=your_gcp_location

# Vertex AI使用フラグ
USE_VERTEX_AI=True # Google AI Studioを使用する場合はFalse

# Geminiモデル名設定
GEMINI_FLASH_MODEL_NAME=gemini-2.5-flash
GEMINI_PRO_MODEL_NAME=gemini-2.5-pro

# Github関連の環境変数
GITHUB_TOKEN=your_github_token
GITHUB_REPO_OWNER=github_repo_ower_name
GITHUB_REPO_NAME=github_repo_name
GITHUB_BRANCH_NAME=github_branch_name

# Vector DBの保存先
CHROMA_DB_PATH=./vector_db
CHROMA_COLLECTION_NAME=supportbot_collection
```

## 3) Vertex AI を使う場合のみ：Service Account JSON を配置
model/service-account.json として配置してください。
（.env の GOOGLE_APPLICATION_CREDENTIALS=/model/service-account.json と整合させるように）

## 4）Dockerコンテナの起動
続いて，Dockerコンテナを作成し起動します．以下のコマンドを実行してください．
```shell:shell
docker compose build --no-cache
docker compose run --rm model
```
上記のコマンドが正常に実行されるとコンテナの内部に入り，該当リポジトリにおけるRAGの構築が始まります．

## 使用方法 (CLI)
起動後に > が表示されたら，質問を入力します．

例：
- verify_token というメソッドは，どのような目的で追加された？
- このリポジトリの認証まわりの設計意図を，PR/Issueの文脈込みで説明して
- 〇〇の変更はどのPRで導入された？その理由は？

終了方法は実装に依存しますが，一般的には Ctrl + C で終了できます

## 補足
### VectorDBのリビルド
ローカルで永続化されている ChromaDB を作り直したい場合は、DBディレクトリを削除して再実行します．

```shell:shell
rm -rf ./vector_db
docker compose run --rm model
```
### Tips
- GitHub Token 権限不足だと、PR/Issue取得で失敗することがあります（参照対象が private の場合は特に注意）
- Rate Limit に達した場合は時間をおいて再実行してください
- Vertex AI 利用時は、GCP側で必要APIの有効化・権限設定が必要です

### セキュリティ関連
- .env や service-account.json は 絶対にコミットしないでください
- 公開リポジトリで扱う場合は .gitignore を必ず確認してください

## ライセンス
MIT LICENSE







