# 育成画面、処理
# _______________________________________________________________________________________
# ==================================================
# インポート
# ==================================================

from flask import Blueprint, render_template, redirect, url_for, request

# Python標準ライブラリ ランダム
import random

from models import db, Ikimono

# ログインしている人だけ利用可能に、現在ログインしているユーザーの取得
from flask_login import login_required, current_user

# ==================================================
# 計算とか
# ==================================================

# 卵と幼体のポイントを合計する
def get_total_points(ikimono):

    total_points = {
        'fuwa': ikimono.egg_fuwa + ikimono.baby_fuwa,
        'shinayaka': ikimono.egg_shinayaka + ikimono.baby_shinayaka,
        'natsuki': ikimono.egg_natsuki + ikimono.baby_natsuki,
        'cool': ikimono.egg_cool + ikimono.baby_cool,
        'fushigi': ikimono.egg_fushigi + ikimono.baby_fushigi
    }
    # total_points という辞書にまとめる

    return total_points


# 特別進化の組み合わせ
SPECIAL_EVOLUTIONS = [
    ('fuwa', 'shinayaka', 'fluffy_water'),
    ('cool', 'fushigi', 'black_cloud'),
    ('fuwa', 'natsuki', 'fluffy_friendly'),
    ('shinayaka', 'fushigi', 'water_cloud')
]


# 特別進化の候補を調べる
def get_special_kouho(total_points):

    kouho = []

    for point_a, point_b, species in SPECIAL_EVOLUTIONS:

        # 2種類の性質が両方とも5以上なら候補にする
        if total_points[point_a] >= 5 and total_points[point_b] >= 5:

            # 2種類のポイントの合計を計算
            score = total_points[point_a] + total_points[point_b]

            kouho.append((score, species))

    return kouho


# 特別進化の候補から1種類を選ぶ
def choose_special_evolution(kouho):

    # 候補がない場合
    if not kouho:
        return None

    # 最も高い合計ポイントを調べる
    highest_score = max(score for score, species in kouho)

    # 最高ポイントと同点の候補を集める
    best_kouho = [
        species
        for score, species in kouho
        if score == highest_score
    ]

    # 同点の場合はランダムに選ぶ
    return random.choice(best_kouho)


# 通常進化の対応表
NORMAL_EVOLUTIONS = {
    'fuwa': 'fluffy',
    'shinayaka': 'sleek',
    'natsuki': 'friendly',
    'cool': 'black',
    'fushigi': 'mysterious'
}

# 成体の種類と日本語名の対応表
SPECIES_NAMES = {
    'fluffy': 'ふわふわ',
    'sleek': 'しなやか',
    'friendly': '人懐っこい',
    'black': '孤高',
    'mysterious': '不思議な生き物',

    'fluffy_water': 'ふわふわ水棲',
    'black_cloud': '暗い雲？',
    'fluffy_friendly': 'ふわふわ人懐っこい生き物',
    'water_cloud': 'ふしぎなしめりけ'
}



# 通常進化の種類を決める
def choose_normal_evolution(total_points):

    # 最も高いポイントを調べる
    highest_score = max(total_points.values())

    # 最高ポイントと同じ性質を集める
    best_points = [
        point
        for point, score in total_points.items()
        if score == highest_score
    ]

    # 同点の場合はランダムに選ぶ
    selected_point = random.choice(best_points)

    # 選ばれた性質に対応する成体を返す
    return NORMAL_EVOLUTIONS[selected_point]


# 最終的な進化先を決める(特別進化を優先させる)
def decide_evolution(ikimono):

    # 卵と幼体のポイントを合計する
    total_points = get_total_points(ikimono)

    # 特別進化の候補を調べる
    kouho = get_special_kouho(total_points)

    # 特別進化の候補がある場合
    if kouho:
        return choose_special_evolution(kouho)

    # 特別進化がない場合は通常進化
    return choose_normal_evolution(total_points)



# ==================================================
# ブループリント
# ==================================================

# 生き物用のBlueprint
ikimono_bp = Blueprint('ikimono', __name__, url_prefix='/ikimono')
    # メモ | Blueprint:機能をまとめるための仕組み、ikimono:Blueprintの名前、__name__:このファイルを基準にする指定、url_prefix='/ikimono':このブループリントでつくるページのURLには/ikimonoがつく。

# ==================================================
# ルーティング
# ==================================================
# ==================================================
# 育成開始
@ikimono_bp.route('/start', methods=['POST'])
@login_required
def start():

    # 現在ログインしているユーザーの育成中の生き物を探す
    active_ikimono = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).first()

    # すでに育成中の生き物がいる場合
    if active_ikimono:
        return "まだ育てている生き物がいます"

    # 新しい卵を作る
    # ここで新しいデータを作り、初期値が入る。
    new_ikimono = Ikimono(
        user_id=current_user.id,
        stage='egg'
    )

    # データベースに登録
    db.session.add(new_ikimono)
    db.session.commit()

    return redirect(url_for('ikimono.egg'))
    # url_for()：指定した関数に対応するURLを取得する
    # redirect()：そのURLへ移動させる

# ==================================================
# 卵の画面
@ikimono_bp.route('/egg')
@login_required
def egg():

    # 現在ログインしているユーザーの育成中の生き物を探す
    active_ikimono = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).first()

    # 育成中の生き物がいない場合はトップページへ戻る
    if active_ikimono is None:
        return redirect(url_for('ikimono.index'))

    return render_template(
        'ikimono/egg.html',
        ikimono=active_ikimono
    )
    
# ==================================================
# 幼体のお部屋
@ikimono_bp.route('/baby')
@login_required
def baby():

    active_ikimono = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=True,
        stage='baby'
    ).first()

    # 幼体が存在しない場合
    if active_ikimono is None:
        return redirect(url_for('ikimono.index'))

    return render_template(
        'ikimono/baby.html',
        ikimono=active_ikimono
    )
    
# ==================================================
# 卵のお世話
@ikimono_bp.route('/care', methods=['POST'])
@login_required
def care():

    # 現在ログインしているユーザーの卵を探す
    active_ikimono = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=True,
        stage='egg'
    ).first()

    print('見つかった生き物：', active_ikimono)

    # 卵が存在しない場合
    if active_ikimono is None:
        print('卵が見つかりませんでした')
        return redirect(url_for('ikimono.index'))

    # お世話が4回終わっている場合
    if active_ikimono.egg_care_count >= 4:

        print('卵のお世話は4回終了しています')

        # 成長段階をbabyに変更
        active_ikimono.stage = 'baby'

        # データベースに保存
        db.session.commit()

        print('幼体のお部屋へ移動します！')

        return redirect(url_for('ikimono.baby'))

    # 押されたボタンの種類を取得
    care_type = request.form.get('care_type')

    print('選ばれたお世話：', care_type)

    # あたためる
    if care_type == 'warm':
        active_ikimono.egg_fuwa += 2
        active_ikimono.egg_natsuki += 1

    # 霧吹きをかける
    elif care_type == 'mist':
        active_ikimono.egg_shinayaka += 2
        active_ikimono.egg_cool += 1

    # 音楽をきかせる
    elif care_type == 'music':
        active_ikimono.egg_natsuki += 1
        active_ikimono.egg_fushigi += 2

    # 見守る
    elif care_type == 'watch':
        active_ikimono.egg_cool += 1

    # 想定外のボタン情報だった場合
    else:
        print('お世話の種類が正しくありません')
        return redirect(url_for('ikimono.egg'))

    # お世話回数を1増やす
    active_ikimono.egg_care_count += 1

    print('増加後のお世話回数：', active_ikimono.egg_care_count)

    # お世話回数が4回になったら幼体に成長
    if active_ikimono.egg_care_count >= 4:

        # 成長段階をbabyに変更
        active_ikimono.stage = 'baby'

        print('卵から幼体に成長しました！')

        # データベースに保存
        db.session.commit()

        return redirect(url_for('ikimono.baby'))

    # データベースに保存
    db.session.commit()

    print('お世話データを保存しました！')

    return redirect(url_for('ikimono.egg'))


# ==================================================
# 幼体のお世話

@ikimono_bp.route('/baby_care', methods=['POST'])
@login_required
def baby_care():

    print('========== 幼体のお世話開始 ==========')

    # 現在ログインしているユーザーの幼体を探す
    active_ikimono = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=True,
        stage='baby'
    ).first()

    print('見つかった生き物：', active_ikimono)

    # 幼体が存在しない場合
    if active_ikimono is None:
        return redirect(url_for('ikimono.index'))

    # お世話が6回終わっている場合
    if active_ikimono.baby_care_count >= 6:

        print('幼体のお世話は6回終了しています')

        return redirect(url_for('ikimono.baby'))

    # 押されたボタンの種類を取得
    care_type = request.form.get('care_type')

    print('選ばれたお世話：', care_type)

    # なでる
    if care_type == 'pet':
        active_ikimono.baby_fuwa += 2
        active_ikimono.baby_natsuki += 1

    # 遊ぶ
    elif care_type == 'play':
        active_ikimono.baby_natsuki += 2
        active_ikimono.baby_fushigi += 1

    # ごはんをあげる
    elif care_type == 'food':
        active_ikimono.baby_natsuki += 1

    # お水をあげる
    elif care_type == 'water':
        active_ikimono.baby_shinayaka += 2

    # 休ませる
    elif care_type == 'rest':
        active_ikimono.baby_cool += 2
        active_ikimono.baby_fushigi += 1

    else:
        print('お世話の種類が正しくありません')
        return redirect(url_for('ikimono.baby'))

    # お世話回数を1増やす
    active_ikimono.baby_care_count += 1

    print('増加後のお世話回数：', active_ikimono.baby_care_count)

    # お世話回数が6回になったら成体に成長
    if active_ikimono.baby_care_count >= 6:

        # 進化先を決める
        species = decide_evolution(active_ikimono)

        # 成体の種類を保存
        active_ikimono.species = species

        # 成長段階をadultに変更
        active_ikimono.stage = 'adult'

        print('幼体から成体に成長しました！')

        # データベースに保存
        db.session.commit()

        return redirect(url_for('ikimono.kekka'))

    # 6回未満の場合もデータベースに保存
    db.session.commit()

    print('お世話データを保存しました！')

    return redirect(url_for('ikimono.baby'))

# ==================================================
# 成体になったときの結果画面
@ikimono_bp.route('/kekka')
@login_required
def kekka():

    active_ikimono = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=True,
        stage='adult'
    ).first()

    # 成体が存在しない場合
    if active_ikimono is None:
        return redirect(url_for('ikimono.index'))

    
    return render_template(
        'ikimono/kekka.html',
        ikimono=active_ikimono,
        species_name=SPECIES_NAMES.get(
            active_ikimono.species,
            '名前のない生き物'
        )
    )

# ==================================================
# 生き物のトップページ
@ikimono_bp.route('/')
@login_required
def index():

    # 現在ログインしているユーザーの育成中の生き物を探す
    active_ikimono = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).first()

    # index.html を表示するときに、active_ikimono という名前で生き物の情報を渡す。
    # (html側でも幾瀬中の生き物がいるかの確認ができるようにする)
    return render_template(
        'ikimono/index.html',
        active_ikimono=active_ikimono
    )
    
# ==================================================
# 成体の名前を登録するルート
@ikimono_bp.route('/register', methods=['POST'])
@login_required
def register():

    active_ikimono = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=True,
        stage='adult'
    ).first()

    # 成体が存在しない場合
    if active_ikimono is None:
        return redirect(url_for('ikimono.index'))

    # 入力された名前を取得する
    name = request.form.get('name', '').strip()

    # 入力された生態メモを取得する
    ecology = request.form.get('ecology', '').strip()
    
    # 名前または生態メモが空の場合
    if not name or not ecology:
        return redirect(url_for('ikimono.kekka'))

    # 名前と生態メモを保存する
    active_ikimono.name = name
    active_ikimono.ecology = ecology

    # 育成を終了する
    active_ikimono.is_active = False

    # データベースに保存
    db.session.commit()

    return redirect(url_for('ikimono.zukan'))

# ==================================================
# 図鑑へのルート
@ikimono_bp.route('/zukan')
@login_required
def zukan():

    # 自分が育て終わった生き物を取得する
    ikimonos = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=False
    ).all()

    # 種類ごとに生き物を分類する
    species_groups = {}

    for ikimono in ikimonos:

        species = ikimono.species

        if species not in species_groups:
            species_groups[species] = []

        species_groups[species].append(ikimono)

    # 種類ごとの日本語名を用意する
    species_names = {}

    for species in species_groups:
        species_names[species] = SPECIES_NAMES.get(
            species,
            '名前のない生き物'
        )
        
    # 種類ごとの代表の生き物を用意する
    representatives = {}

    for species in species_groups:

        representative = Ikimono.query.filter_by(
            user_id=current_user.id,
            is_active=False,
            species=species,
            is_representative=True
        ).first()

        representatives[species] = representative


    return render_template(
        'ikimono/zukan.html',
        species_groups=species_groups,
        species_names=species_names,
        representatives=representatives
    )
# ==================================================    
# 種類ごとの図鑑ページ
@ikimono_bp.route('/zukan/<species>')
@login_required
def species_detail(species):

    # 選択された種類の生き物を取得する
    ikimonos = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=False,
        species=species
    ).all()

    # 種類名を日本語にする
    species_name = SPECIES_NAMES.get(
        species,
        '名前のない生き物'
    )

    return render_template(
        'ikimono/species.html',
        ikimonos=ikimonos,
        species_name=species_name
    )
    
    # 種類ごとの代表の生き物を用意する
    representatives = {}

    for species in species_groups:

        representative = Ikimono.query.filter_by(
            user_id=current_user.id,
            is_active=False,
            species=species,
            is_representative=True
        ).first()

        representatives[species] = representative
    
# ==================================================  
# 図鑑の代表の生き物の設定
@ikimono_bp.route(
    '/zukan/<species>/representative/<int:ikimono_id>',
    methods=['POST']
)
@login_required
def set_representative(species, ikimono_id):

    # 選択された生き物を取得する
    ikimono = Ikimono.query.filter_by(
        id=ikimono_id,
        user_id=current_user.id,
        is_active=False,
        species=species
    ).first()

    # 生き物が見つからなければ図鑑に戻る
    if ikimono is None:
        return redirect(url_for('ikimono.zukan'))

    # 同じ種類の代表設定をいったん解除する
    ikimonos = Ikimono.query.filter_by(
        user_id=current_user.id,
        is_active=False,
        species=species
    ).all()

    for item in ikimonos:
        item.is_representative = False

    # 選択した生き物を代表にする
    ikimono.is_representative = True

    db.session.commit()

    return redirect(url_for(
        'ikimono.species_detail',
        species=species
    ))

# ==================================================
# 生き物の個体詳細ページ
# URLに含まれる個体IDを使って、特定の1匹だけを取得できるようにしていく。
@ikimono_bp.route('/kobetu/<int:ikimono_id>')
@login_required
def kobetu(ikimono_id):

    # 選択された生き物を取得する
    ikimono = Ikimono.query.filter_by(
        id=ikimono_id,
        user_id=current_user.id,
        is_active=False
    ).first()

    # 生き物が見つからなければ図鑑に戻る
    if ikimono is None:
        return redirect(url_for('ikimono.zukan'))

    species_name = SPECIES_NAMES.get(
        ikimono.species,
        '名前のない生き物'
    )

    return render_template(
        'ikimono/kobetu.html',
        ikimono=ikimono,
        species_name=species_name
    )


# ==================================================
# 図鑑の個体情報を編集できるように

@ikimono_bp.route(
    '/kobetu/<int:ikimono_id>/edit',
    methods=['POST']
)
@login_required
def edit_kobetu(ikimono_id):

    # 編集する生き物を取得する
    # 自分が育て終わった生き物だけを対象にする
    # 編集対象の生き物を探している。
    # ユーザーIDも確認しているので、他の人の生き物を編集することはできない。
    ikimono = Ikimono.query.filter_by(
        id=ikimono_id,
        user_id=current_user.id,
        is_active=False
    ).first()

    # 生き物が見つからなければ図鑑に戻る
    if ikimono is None:
        return redirect(url_for('ikimono.zukan'))

    # フォームから新しい名前と生態メモを取得する
    # HTMLフォームから送られてきた名前と生態メモを取得。
    # .strip() は、文章の前後にある余分な空白を取り除くもの
    name = request.form.get('name', '').strip()
    ecology = request.form.get('ecology', '').strip()

    # 名前が空の場合は編集ページに戻る
    if not name:
        return redirect(url_for(
            'ikimono.kobetu',
            ikimono_id=ikimono.id
        ))

    # 新しい情報にでーたべーすの更新
    ikimono.name = name
    ikimono.ecology = ecology

    # データベースに保存する
    db.session.commit()

    # 編集した個体の詳細ページに戻る
    return redirect(url_for(
        'ikimono.kobetu',
        ikimono_id=ikimono.id
    ))

