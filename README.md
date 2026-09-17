# Sistem Informasi Transkrip Nilai (Flask + MySQL)

Instruksi singkat untuk menjalankan aplikasi lokal:

1. Siapkan MySQL dan buat database `transkrip_db` (atau set `DATABASE_URL`).
2. Buat virtualenv dan install dependensi:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Jalankan skrip inisialisasi DB:

```bash
python create_db.py
```

4. Jalankan aplikasi:

```bash
python app.py
```

Default akun sample:
- Mahasiswa: NIK `07352311052`, password `mahasiswa123`
- Tata Usaha: NIK `admin001`, password `adminpass`

Catatan: Sesuaikan `DATABASE_URL` dan `SECRET_KEY` melalui environment variable.
