from flask import Flask, render_template, json, request, Response
import config
from datetime import datetime
from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.orm import Session

engine = create_engine(config.conexao_banco)

app = Flask(__name__)

@app.get('/')
def index():
    hoje = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/index.html', hoje=hoje)

@app.get('/sobre')
def sobre():
    return render_template('index/sobre.html', titulo='Sobre Nós')

@app.get('/detalhes')
def detalhes():
    return render_template('index/detalhes.html', titulo='Detalhes do jogo')

@app.get('/pesquisa')
def pesquisa():
    return render_template('index/pesquisa.html', titulo='Procurar')

@app.get('/obterDados')
def obterDados():
    dados = {
        'kpis': {},
        'top_userscore': [],
        'top_metascore': [],
        'top_generos_media_meta': [],
        'top_publishers_media_meta': [],
        'top_discrepancia': [],
        'meta_por_decada': []
    }

    # ---- filtros vindos do front ----
    genres = request.args.getlist('genre')
    publishers = request.args.getlist('publisher')
    year_min = request.args.get('year_min', type=int)
    year_max = request.args.get('year_max', type=int)
    meta_min = request.args.get('meta_min', type=int)
    meta_max = request.args.get('meta_max', type=int)

    where = []
    params = {}

    # OBS: usamos aliases g (game), ge (genre), p (publisher) em todas as queries
    if genres:
        where.append("ge.genre_name IN :genres")
        params["genres"] = genres

    if publishers:
        where.append("p.publisher_name IN :publishers")
        params["publishers"] = publishers

    if year_min is not None:
        where.append("YEAR(g.game_launch) >= :year_min")
        params["year_min"] = year_min

    if year_max is not None:
        where.append("YEAR(g.game_launch) <= :year_max")
        params["year_max"] = year_max

    if meta_min is not None:
        where.append("g.game_meta >= :meta_min")
        params["meta_min"] = meta_min

    if meta_max is not None:
        where.append("g.game_meta <= :meta_max")
        params["meta_max"] = meta_max

    dynamic_where_sql = (" AND " + " AND ".join(where)) if where else ""

    # bindparams (expanding) para IN :genres / IN :publishers
    def bind_expanding(q: str):
        stmt = text(q)
        if genres:
            stmt = stmt.bindparams(bindparam("genres", expanding=True))
        if publishers:
            stmt = stmt.bindparams(bindparam("publishers", expanding=True))
        return stmt

    with engine.begin() as conn:
        # ---------------- KPIs ----------------
        kpi_stmt = bind_expanding(f"""
            SELECT
                COUNT(*) AS total_games,
                AVG(g.game_meta) AS avg_metascore,
                AVG(g.game_user) AS avg_userscore,
                COUNT(DISTINCT g.publisher_id) AS total_publishers
            FROM game g
            LEFT JOIN genre ge ON ge.genre_id = g.genre_id
            LEFT JOIN publisher p ON p.publisher_id = g.publisher_id
            WHERE 1=1 {dynamic_where_sql}
        """)

        kpi = conn.execute(kpi_stmt, params).mappings().first()

        dados['kpis'] = {
            'total_games': int(kpi['total_games'] or 0),
            'avg_metascore': float(kpi['avg_metascore']) if kpi['avg_metascore'] is not None else 0,
            'avg_userscore': float(kpi['avg_userscore']) if kpi['avg_userscore'] is not None else 0,
            'total_publishers': int(kpi['total_publishers'] or 0),
        }

        # ---------------- Top UserScore ----------------
        top_user_stmt = bind_expanding(f"""
            SELECT g.game_name, g.game_user
            FROM game g
            LEFT JOIN genre ge ON ge.genre_id = g.genre_id
            LEFT JOIN publisher p ON p.publisher_id = g.publisher_id
            WHERE g.game_user IS NOT NULL {dynamic_where_sql}
            ORDER BY g.game_user DESC
            LIMIT 10
        """)
        registros = conn.execute(top_user_stmt, params)
        for r in registros:
            dados['top_userscore'].append({
                'game_name': r[0],
                'score': float(r[1])
            })

        # ---------------- Top MetaScore ----------------
        top_meta_stmt = bind_expanding(f"""
            SELECT g.game_name, g.game_meta
            FROM game g
            LEFT JOIN genre ge ON ge.genre_id = g.genre_id
            LEFT JOIN publisher p ON p.publisher_id = g.publisher_id
            WHERE g.game_meta IS NOT NULL {dynamic_where_sql}
            ORDER BY g.game_meta DESC
            LIMIT 10
        """)
        registros = conn.execute(top_meta_stmt, params)
        for r in registros:
            dados['top_metascore'].append({
                'game_name': r[0],
                'score': int(r[1])
            })

        # ---------------- Média MetaScore por Gênero ----------------
        genre_stmt = bind_expanding(f"""
            SELECT
                ge.genre_name,
                AVG(g.game_meta) AS media_meta,
                COUNT(*) AS qtd_jogos
            FROM game g
            JOIN genre ge ON ge.genre_id = g.genre_id
            LEFT JOIN publisher p ON p.publisher_id = g.publisher_id
            WHERE g.game_meta IS NOT NULL
              AND g.genre_id IS NOT NULL
              {dynamic_where_sql}
            GROUP BY ge.genre_id, ge.genre_name
            HAVING COUNT(*) >= 5
            ORDER BY media_meta DESC
            LIMIT 10
        """)
        registros = conn.execute(genre_stmt, params)
        for r in registros:
            dados['top_generos_media_meta'].append({
                'genre_name': r[0],
                'media_meta': float(r[1]),
                'qtd_jogos': int(r[2])
            })

        # ---------------- Média MetaScore por Publisher ----------------
        pub_stmt = bind_expanding(f"""
            SELECT
                p.publisher_name,
                AVG(g.game_meta) AS media_meta,
                COUNT(*) AS qtd_jogos
            FROM game g
            JOIN publisher p ON p.publisher_id = g.publisher_id
            LEFT JOIN genre ge ON ge.genre_id = g.genre_id
            WHERE g.game_meta IS NOT NULL
              AND g.publisher_id IS NOT NULL
              {dynamic_where_sql}
            GROUP BY p.publisher_id, p.publisher_name
            HAVING COUNT(*) >= 5
            ORDER BY media_meta DESC
            LIMIT 10
        """)
        registros = conn.execute(pub_stmt, params)
        for r in registros:
            dados['top_publishers_media_meta'].append({
                'publisher_name': r[0],
                'media_meta': float(r[1]),
                'qtd_jogos': int(r[2])
            })

        # ---------------- Discrepância (ABS) ----------------
        disc_stmt = bind_expanding(f"""
            SELECT
                g.game_name,
                g.game_meta,
                g.game_user,
                ABS(g.game_meta - (g.game_user * 10)) AS discrepancia
            FROM game g
            LEFT JOIN genre ge ON ge.genre_id = g.genre_id
            LEFT JOIN publisher p ON p.publisher_id = g.publisher_id
            WHERE g.game_meta IS NOT NULL
              AND g.game_user IS NOT NULL
              {dynamic_where_sql}
            ORDER BY discrepancia DESC
            LIMIT 10
        """)
        registros = conn.execute(disc_stmt, params)
        for r in registros:
            dados['top_discrepancia'].append({
                'game_name': r[0],
                'metascore': int(r[1]),
                'userscore': float(r[2]),
                'discrepancia': float(r[3])
            })

        # ---------------- MetaScore por década ----------------
        dec_stmt = bind_expanding(f"""
            SELECT
                (FLOOR(YEAR(g.game_launch)/10) * 10) AS decada,
                AVG(g.game_meta) AS media_meta,
                COUNT(*) AS qtd_jogos
            FROM game g
            LEFT JOIN genre ge ON ge.genre_id = g.genre_id
            LEFT JOIN publisher p ON p.publisher_id = g.publisher_id
            WHERE g.game_launch IS NOT NULL
              AND g.game_meta IS NOT NULL
              {dynamic_where_sql}
            GROUP BY decada
            ORDER BY decada ASC
        """)
        registros = conn.execute(dec_stmt, params)
        for r in registros:
            decada_num = int(r[0])
            dados['meta_por_decada'].append({
                'decada': f"{decada_num}s",
                'decada_inicio': decada_num,
                'media_meta': float(r[1]),
                'qtd_jogos': int(r[2])
            })

    return json.jsonify(dados)

@app.get('/obterGeneros')
def obterGeneros():
    generos = []
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT genre_name
            FROM genre
            ORDER BY genre_name
        """))
        for r in rows:
            generos.append(r[0])
    return json.jsonify({'generos': generos})


@app.post('/criar')
def criar():
    dados = request.json
    print(dados['id'])
    print(dados['nome'])
    return Response(status=204)

if __name__ == '__main__':
    app.run(host=config.host, port=config.port)
