# 土台
# やることメモ ･･･ ・スマホ対応
#                 ・web公開
#                 ・ブループリント
# 
# 他 memo:　・お世話をした回数や蓄積したポイントによって育つ。
#    　 　  ・同時に育てられるのは１匹まで
# _______________________________________________________________________________________

from flask import Flask
# Webアプリケーションの本体
from flask_migrate import Migrate
# Flask-Migrateを使い、データベースのマイグレーション（テーブル構造の変更管理）を行えるように``

from models import db, User
# models.py からSQLAlchemyのデータベースインスタンスとユーザーモデルを読み込み
from flask_login import LoginManager
# Flask-Loginを使い、ユーザーのログイン状態やセッションを管理

from auth.views import auth_bp
from memo.views import memo_bp
from ikimono.views import ikimono_bp 
# 認証（auth）、メモ（memo）、生き物（ikimono）の各機能ごとに分割されたルーティング（Blueprint）を読み込み 


# ==================================================
# Flask
# ==================================================
app = Flask(__name__)
# 設定ファイル読み込み
app.config.from_object("config.Config")
# dbとFlaskとの紐づけ
db.init_app(app)
# マイグレーションとの紐づけ（Flaskとdb）
migrate = Migrate(app, db)

# LoginManagerインスタンス
# ログインマネージャーの初期化
login_manager = LoginManager()
# LoginManagerとFlaskとの紐づけ
login_manager.init_app(app)
# ログインが必要なページにアクセスしようとしたときに表示されるメッセージを変更
login_manager.login_message = "認証していません：ログインしてください"
# 未認証のユーザーがアクセスしようとした際に
# リダイレクトされる関数名を設定する(ブループリント対応)
login_manager.login_view = 'auth.login'  # 未ログイン時のリダイレクト先

# blueprintをアプリケーションに登録
app.register_blueprint(auth_bp)
app.register_blueprint(memo_bp)
app.register_blueprint(ikimono_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# viewsのインポート
from views import *

# ==================================================
# 実行
# ==================================================
if __name__ == "__main__":
    app.run()