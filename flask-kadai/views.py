# 🌟リファクタリング済
# 　　　リファクタリング･･･コードを改善して理解しやすくする。内容は変えない。

from flask import render_template
from app import app

# ==================================================
# ルーティング
# ==================================================
# モジュールのインポート
from werkzeug.exceptions import NotFound

# エラーハンドリング
@app.errorhandler(NotFound)
def show_404_page(error):
    msg = error.description
    print('エラー内容：',msg)
    return render_template('errors/404.html', msg=msg) , 404
