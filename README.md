# フロー図
<img src="flowchart.png" alt="フロー図">


# フォルダー構築
> KerasNodeJs<br/>
>　|_ KerasServer（サーバー側）<br/>
>　|　　　|_ bridge（公開なし）<br/>
>　|　　　|_ nginx（公開なし）<br/>
>　|　　　|_ nodejs（サーバーサイド）<br/>
>　|　　　|_ uwsgi（APIサービス）<br/>
>　|_ KerasClient（画像認識学習側）<br/>
>　|　　　|_ traindata（公開なし）<br/>
>　|　　　|_ trainapp（AIワーカー）
>　|_ KerasApp（スマホ向けのAIアプリ-公開なし）<br/>
>
> ※docker-compose.yml、Dockerfileなども公開なし

# 説明
### ① サーバー側
※Nginx + uWSGI + FlaskでAPIサービスを動かす。
- nginx: Nginxを通じてHTTPクライアントからのリクエストをuWSGIに転送する。
- uwsgi: APIサービス（uWSGI + Flask）として下記を処理させて、クライアント側へ結果を返却する。
    - ログインAPI、ログアウトAPI
    - 学習状況監視、画像データ閲覧などのデータ抽出API
    - データ更新API
    - データ登録API
    - データ削除API
    - 学習データアップロードAPI
    - 学習データダウンロードAPI
- bridge: H5, MLModel等の学習ファイルを管理する。
- 環境構築：Docker, Nginx, uWSGI, Flask
- 開発言語：Python 3.8


### ② クライアント側
- ブラウザー<br/>
    - nodejs: Node.jsフレームワークを用いてOracle JET Webアプリケーションである。<br/>
    1. ログインできた場合は暗号化済みクッキー情報をクライアント側へ返却する。<br/>
    2. サーバー側ではNginxを通じて自動でログイン状況が認証されるため、<br/>
    クライアント側のクッキー情報が無断で編集された場合は、自動でログイン画面へ遷移される。
    - 環境構築: Node.js
    - 開発言語: Oracle JET, Knockout, Linq


### ③ 画像認識学習側（クラウド側）
- traindata: 学習用画像データ保存フォルダーである。
- trainapp: AIワーカーとして画像データ学習を行うアプリケーションである。<br/>
1. 複数のAIワーカーが同時に学習できるが、同時学習可能な回数を超える場合は、<br/>
メモリがオーバーされる可能性があるため、スキップとする。<br/>
2. 画像データ学習終了後、学習結果(H5, MLModelなど)をサーバー側（FTPサーバー）へ再送して、<br/>クライアント側で学習データを全て削除する。
- 開発言語: Python 3.8 (Celery, Keras 2.3.1, Tensorflow 1.15.3), Redis

