# データベース系
# _______________________________________________________________________________________

from flask_sqlalchemy import SQLAlchemy
# Flaskでデータベース（SQLAlchemy）を簡単に扱うための拡張機能。Pythonのクラスをそのままテーブル定義（ORM）として扱える。

from werkzeug.security import generate_password_hash, check_password_hash
# パスワードを安全にハッシュ化（暗号化の一種で元に戻せない形式に変換）したり、
# ログイン時に入力されたパスワードがハッシュ値と一致するか検証したりするための関数

from flask_login import UserMixin
# Flaskでログイン状態を管理する「Flask-Login」のクラス。
# 自作のUserモデルに継承させるだけで、is_authenticated や get_id といったログイン管理に必須のプロパティやメソッドを自動で備えさせることができる。

from sqlalchemy.orm import relationship
# データベースのテーブル同士（例：ユーザーと投稿、ユーザーとToDoなど）の「1対多」や「多対多」といったリレーション（関連付け）を定義。

# Flask-SQLAlchemyの生成
db = SQLAlchemy()

# ==================================================
# モデル
# ==================================================
# メモ
class Memo(db.Model):
    # テーブル名
    __tablename__ = 'memos'
    # ID（PK）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # タイトル（NULL許可しない）
    title = db.Column(db.String(50), nullable=False)
    # 内容
    content = db.Column(db.Text)

    # ユーザーID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name="fk_memos_users"), nullable=False)

    # User とのリレーション
    user = relationship("User", back_populates = "memos")


# 空欄を許可しない設定　nullable=False、空欄でもよい設定　nullable=True
# （卵から育成を始めるなら True）
# 生き物
class Ikimono(db.Model):
    # データベースに作るテーブルの名前
    __tablename__ = 'ikimonos'

    # 生き物ごとの識別番号。テーブルに保存する項目の定義。
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 育てているユーザーのID
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    
    # User とのリレーション(ユーザー側の ikimonos と、生き物側の user を対応させる)
    user = relationship("User", back_populates="ikimonos")

    # 成長段階と生き物の種類
      # 最初は egg  
    stage = db.Column(db.String(20), default='egg', nullable=False)
      # 
    species = db.Column(db.String(50), nullable=True)

    # 卵のときの育成ポイント
    # 新しい生き物を作るとき、指定がなければ最初は0になる。(default=0)
    egg_fuwa = db.Column(db.Integer, default=0, nullable=False)
    egg_shinayaka = db.Column(db.Integer, default=0, nullable=False)
    egg_natsuki = db.Column(db.Integer, default=0, nullable=False)
    egg_cool = db.Column(db.Integer, default=0, nullable=False)
    egg_fushigi = db.Column(db.Integer, default=0, nullable=False)

    # 幼体のときの育成ポイント
    baby_fuwa = db.Column(db.Integer, default=0, nullable=False)
    baby_shinayaka = db.Column(db.Integer, default=0, nullable=False)
    baby_natsuki = db.Column(db.Integer, default=0, nullable=False)
    baby_cool = db.Column(db.Integer, default=0, nullable=False)
    baby_fushigi = db.Column(db.Integer, default=0, nullable=False)

    # お世話した回数
    egg_care_count = db.Column(db.Integer, default=0, nullable=False)
    baby_care_count = db.Column(db.Integer, default=0, nullable=False)

    # 図鑑に登録する情報
    name = db.Column(db.String(50), nullable=True)
    ecology = db.Column(db.Text, nullable=True)

    # 育成中か、図鑑登録済みか
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # 図鑑の代表の子かどうか
    is_representative = db.Column(db.Boolean, default=False, nullable=False)

    
# ユーザー
class User(UserMixin, db.Model):
    # テーブル名
    __tablename__ = 'users'
    # ID（PK）    
    id = db.Column(db.Integer, primary_key=True)
    # ユーザー名
    username = db.Column(db.String(50), unique=True, nullable=False)
    # パスワード
    password = db.Column(db.String(120), nullable=False)
    
    # Memo とのリレーション
    # リレーション: １対多
    memos = relationship("Memo", back_populates = "user")
    
    # Ikimono とのリレーション
    # リレーション: １対多 (一人につきいっぱい図鑑登録可)
    ikimonos = relationship("Ikimono", back_populates="user")
    
    # パスワードをハッシュ化して設定する
    def set_password(self, password):
        self.password = generate_password_hash(password)
    # 入力したパスワードとハッシュ化されたパスワードの比較
    def check_password(self, password):
        return check_password_hash(self.password, password)