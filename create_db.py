import os
import pymysql
from urllib.parse import urlparse
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
from sqlalchemy.engine import make_url

app = create_app()

def ensure_database(uri):
    # Parse DB URI and create database if missing
    url = make_url(uri)
    db_name = url.database
    if not db_name:
        return

    host = url.host or '127.0.0.1'
    port = url.port or 3306
    username = url.username or 'root'
    password = url.password or ''

    try:
        conn = pymysql.connect(host=host, user=username, password=password, port=port)
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        conn.close()
        print(f"Database '{db_name}' ensured (created if missing).")
    except Exception as e:
        print('Gagal membuat/mengecek database:', e)

with app.app_context():
    # Ensure database exists before creating tables
    ensure_database(app.config.get('SQLALCHEMY_DATABASE_URI'))
    db.create_all()

    # Create sample mahasiswa with NIK 07352311052
    if not User.query.filter_by(nik='07352311052').first():
        u = User(
            nik='07352311052',
            name='Contoh Mahasiswa',
            role='mahasiswa',
            password_hash=generate_password_hash('mahasiswa123')
        )
        db.session.add(u)

    # Create sample tata usaha
    if not User.query.filter_by(nik='admin001').first():
        a = User(
            nik='admin001',
            name='Tata Usaha',
            role='tata_usaha',
            password_hash=generate_password_hash('adminpass')
        )
        db.session.add(a)

    db.session.commit()
    print('Database initialized with sample users.')

