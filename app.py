import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Transcript

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'tata_usaha':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('student_dashboard'))
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            nik = request.form['nik']
            password = request.form['password']
            user = User.query.filter_by(nik=nik).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                flash('Berhasil login', 'success')
                return redirect(url_for('index'))
            flash('NIK atau password salah', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if current_user.role != 'tata_usaha':
            abort(403)
        students = User.query.filter_by(role='mahasiswa').all()
        return render_template('admin_dashboard.html', students=students)

    @app.route('/admin/student/<int:user_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_student(user_id):
        if current_user.role != 'tata_usaha':
            abort(403)
        student = User.query.get_or_404(user_id)
        if request.method == 'POST':
            student.name = request.form['name']
            student.nik = request.form['nik']
            if request.form.get('password'):
                student.password_hash = generate_password_hash(request.form['password'])
            db.session.commit()
            flash('Data mahasiswa diperbarui', 'success')
            return redirect(url_for('admin_dashboard'))
        return render_template('edit_student.html', student=student)

    @app.route('/admin/student/create', methods=['GET', 'POST'])
    @login_required
    def create_student():
        if current_user.role != 'tata_usaha':
            abort(403)
        if request.method == 'POST':
            nik = request.form['nik']
            name = request.form['name']
            password = request.form['password']
            if User.query.filter_by(nik=nik).first():
                flash('NIK sudah terdaftar', 'danger')
                return redirect(url_for('create_student'))
            u = User(nik=nik, name=name, role='mahasiswa', password_hash=generate_password_hash(password))
            db.session.add(u)
            db.session.commit()
            flash('Mahasiswa dibuat', 'success')
            return redirect(url_for('admin_dashboard'))
        return render_template('create_student.html')

    @app.route('/admin/upload/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def upload_transcript(user_id):
        if current_user.role != 'tata_usaha':
            abort(403)
        student = User.query.get_or_404(user_id)
        if request.method == 'POST':
            file = request.files.get('file')
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{student.nik}_{file.filename}")
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                t = Transcript(user_id=student.id, filename=filename)
                db.session.add(t)
                db.session.commit()
                flash('Transkrip berhasil diunggah', 'success')
                return redirect(url_for('admin_dashboard'))
            flash('File tidak valid', 'danger')
        return render_template('upload.html', student=student)

    @app.route('/student')
    @login_required
    def student_dashboard():
        if current_user.role != 'mahasiswa':
            abort(403)
        transcripts = current_user.transcripts
        return render_template('student_dashboard.html', transcripts=transcripts)

    @app.route('/transcript/<int:tid>')
    @login_required
    def view_transcript(tid):
        t = Transcript.query.get_or_404(tid)
        # students can only view their own transcripts; tata usaha can view all
        if current_user.role == 'mahasiswa' and t.user_id != current_user.id:
            abort(403)
        # remove inline viewing; force download only
        return redirect(url_for('download_file', filename=t.filename))

    @app.route('/download/<filename>')
    @login_required
    def download_file(filename):
        # Ensure user has access
        t = Transcript.query.filter_by(filename=filename).first()
        if not t:
            abort(404)
        if current_user.role == 'mahasiswa' and t.user_id != current_user.id:
            abort(403)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
