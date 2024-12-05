import pytest
from app import app, get_db_connection
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL
        );
    """)
    conn.commit()
    conn.close()



def test_register_and_login(client):
    response = client.post('/register', data={
        'username': 'test_user',
        'password': 'password123'
    })
    assert response.status_code == 302

    # Вход
    response = client.post('/login', data={
        'username': 'test_user',
        'password': 'password123'
    })
    assert response.status_code == 302


def test_create_article(client):

    client.post('/login', data={
        'username': 'test_user',
        'password': 'password123'
    })

    response = client.post('/articles/create', data={
        'title': 'Тестовая статья',
        'content': 'ТестировочкаТестировочкаТестировочка'
    })
    assert response.status_code == 302

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM articles WHERE title = %s", ('Test Article',))
    article = cur.fetchone()
    conn.close()
    assert article is not None
    assert article[1] == 'Test Article'


def test_access_control(client):
    response = client.get('/articles/create')
    assert response.status_code == 302
