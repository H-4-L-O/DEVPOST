from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import pymysql
from werkzeug.utils import secure_filename
import os
import pymysql.cursors

# Flask 앱 생성 및 시크릿 키 설정 (플래시 메시지용)
app = Flask(__name__)
app.secret_key = 'DEVTABLE_practice’'


# 파일 업로드 설정
UPLOAD_FOLDER = './uploads1'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DB 연결 함수
def db_connect():
    """MySQL 데이터베이스 연결을 반환하는 함수"""
    return pymysql.connect(
        host='mysql',
        user='halo',
        password='1234',
        database='DEVPOST',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor  # DictCursor 추가
    )

# 파일 업로드 설정
UPLOAD_FOLDER = './static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 내 프로필 페이지 (정보 수정 및 프로필 이미지 업로드)
@app.route('/profile', methods=['GET', 'POST'])
def my_profile():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = db_connect()

    if request.method == 'POST':  # 정보 수정 및 프로필 이미지 업로드 처리
        name = request.form['name']
        school = request.form['school']
        profile_image = request.files.get('profile_image')

        relative_path = None
        if profile_image and profile_image.filename:
            filename = secure_filename(profile_image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(image_path)

            # 'static/' 이후의 경로만 저장
            relative_path = os.path.relpath(image_path, 'static')

        with conn.cursor() as cursor:
            query = """
            UPDATE MEMBERS
            SET MEMBER_name = %s, School = %s, USER_profile = %s
            WHERE MEMBER_id = %s
            """
            cursor.execute(query, (name, school, relative_path, user_id))  # relative_path 사용
            conn.commit()

        flash('프로필 정보가 수정되었습니다.', 'success')
        return redirect(url_for('my_profile'))

    # GET 요청: 현재 사용자 정보 가져오기
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM MEMBERS WHERE MEMBER_id = %s", (user_id,))
        user = cursor.fetchone()
    conn.close()

    return render_template('my_profile.html', user=user)


# 다른 사용자의 프로필 보기
@app.route('/profile/<int:user_id>')
def view_profile(user_id):
    conn = db_connect()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM MEMBERS WHERE MEMBER_id = %s", (user_id,))
        user = cursor.fetchone()
    conn.close()

    if not user:
        flash('해당 회원을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('index'))

    return render_template('view_profile.html', user=user)

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        school = request.form['school']
        email = request.form['email']
        user_id = request.form['user_id']
        password = request.form['password']

        conn = db_connect()
        with conn.cursor() as cursor:
            try:
                query = """
                INSERT INTO MEMBERS (MEMBER_name, School, User_email, User_id, User_password)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (name, school, email, user_id, password))
                conn.commit()
                flash('회원가입이 완료되었습니다.', 'success')
                return redirect(url_for('login'))
            except pymysql.MySQLError as e:
                flash(f'오류 발생: {str(e)}', 'danger')
        conn.close()
    return render_template('register.html')

# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        conn = db_connect()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM MEMBERS WHERE User_id = %s AND User_password = %s", (user_id, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user['MEMBER_id']
                session['user_name'] = user['MEMBER_name']
                flash('로그인 성공!', 'success')
                return redirect(url_for('index'))
            else:
                flash('로그인 실패: 아이디 또는 비밀번호를 확인하세요.', 'danger')
        conn.close()
    return render_template('login.html')

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))

# id 찾기
@app.route('/find_id', methods=['GET', 'POST'])
def find_id():
    if request.method == 'POST':
        name = request.form['name']
        school = request.form['school']
        email = request.form['email']

        conn = db_connect()
        with conn.cursor() as cursor:
            # 이름, 학교, 이메일에 매칭되는 아이디 검색
            cursor.execute(
                "SELECT User_id FROM MEMBERS WHERE MEMBER_name = %s AND School = %s AND User_email = %s",
                (name, school, email)
            )
            user = cursor.fetchone()
        conn.close()

        if user:
            # 아이디를 팝업으로 출력
            return f"""
            <script>
                alert('찾으신 아이디는: {user['User_id']} 입니다.');
                window.location.href = '/find_id';
            </script>
            """
        else:
            # 정보가 없을 경우 팝업 출력
            return """
            <script>
                alert('등록된 정보가 없습니다.');
                window.location.href = '/find_id';
            </script>
            """

    return render_template('find_id.html')


# 비밀번호 찾기
@app.route('/find_password', methods=['GET', 'POST'])
def find_password():
    if request.method == 'POST':
        user_id = request.form['user_id']
        name = request.form['name']
        school = request.form['school']
        email = request.form['email']

        conn = db_connect()
        with conn.cursor() as cursor:
            # 아이디, 이름, 학교, 이메일에 매칭되는 비밀번호 검색
            cursor.execute(
                """
                SELECT User_password FROM MEMBERS
                WHERE User_id = %s AND MEMBER_name = %s AND School = %s AND User_email = %s
                """,
                (user_id, name, school, email)
            )
            user = cursor.fetchone()
        conn.close()

        if user:
            # 비밀번호를 팝업으로 출력
            return f"""
            <script>
                alert('찾으신 비밀번호는: {user['User_password']} 입니다.');
                window.location.href = '/find_password';
            </script>
            """
        else:
            # 정보가 없을 경우 팝업 출력
            return """
            <script>
                alert('등록된 정보가 없습니다.');
                window.location.href = '/find_password';
            </script>
            """

    return render_template('find_password.html')



# 메인 페이지 - 게시글 목록 표시
@app.route('/')
def index():
    """
    게시판 메인 페이지로 이동.
    POST_TABLE 테이블에서 모든 게시물을 작성 시간 기준으로 내림차순 정렬하여 표시.
    각 게시글에 작성자 정보 포함.
    """
    conn = db_connect()
    with conn.cursor() as cursor:
        cursor.execute("""
        SELECT p.POST_id, p.POST_title, p.Create_time, m.MEMBER_name, m.MEMBER_id
        FROM POST_TABLE p
        JOIN MEMBERS m ON p.MEMBER_id = m.MEMBER_id
        ORDER BY p.Create_time DESC
        """)
        posts = cursor.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


# 게시글 생성
@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        password = request.form.get('password') 
        file = request.files.get('file')

        file_path = None
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        conn = db_connect()
        with conn.cursor() as cursor:
            query = """
            INSERT INTO POST_TABLE (POST_title, POST_contents, POST_password, File_path, MEMBER_id)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (title, content, password, file_path, session['user_id']))
            conn.commit()
        conn.close()
        flash('게시글 작성 완료', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html')


# 게시글 읽기
@app.route('/read/<int:post_id>', methods=['GET', 'POST'])
def read_post(post_id):
    """
    특정 게시글 읽기.
    POST_id를 기반으로 데이터베이스에서 게시글 정보를 가져와 상세 페이지로 전달.
    """
    conn = db_connect()
    with conn.cursor() as cursor:
        # 게시글과 작성자 정보를 함께 조회
        cursor.execute("""
        SELECT p.*, m.MEMBER_name, m.USER_profile, m.MEMBER_id
        FROM POST_TABLE p
        JOIN MEMBERS m ON p.MEMBER_id = m.MEMBER_id
        WHERE p.POST_id = %s
        """, (post_id,))
        post = cursor.fetchone()
    conn.close()

    # 게시글이 없을 경우 처리
    if not post:
        flash('해당 게시글이 존재하지 않습니다.', 'danger')
        return redirect(url_for('index'))

    # 비밀글인 경우 비밀번호 확인
    if post['POST_password']:
        if request.method == 'POST':
            input_password = request.form['password']
            if input_password == post['POST_password']:
                return render_template('read_post.html', post=post)
            else:
                flash('비밀번호가 틀렸습니다.', 'danger')
                return redirect(url_for('read_post', post_id=post_id))
        return render_template('password_prompt.html', post_id=post_id)
    
    # 비밀번호가 없는 일반 게시글
    return render_template('read_post.html', post=post)


# 게시글 다운로드
@app.route('/download/<filename>')
def download(filename):
    """
    업로드된 파일 다운로드.
    """
    try:
        # 다운로드를 위해 파일을 업로드 폴더에서 검색
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        flash('파일을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('index'))


# 게시글 수정
@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
def update_post(post_id):
    """
    특정 게시글 수정.
    POST 요청 시 제목, 내용, 파일을 수정하고 메인 페이지로 리다이렉트.
    GET 요청 시 수정 페이지 표시.
    """
    conn = db_connect()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files.get('file')

        # 파일 경로 처리
        file_path = None
        if file and file.filename:  # 새 파일 업로드가 있는 경우
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        # 기존 게시글 가져오기 (기존 파일 경로 유지용)
        with conn.cursor() as cursor:
            cursor.execute("SELECT File_path FROM POST_TABLE WHERE POST_id = %s", (post_id,))
            old_post = cursor.fetchone()

        # 기존 파일 삭제 (새 파일이 업로드된 경우)
        if file_path and old_post['File_path']:
            old_file_path = old_post['File_path']
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        # 게시글 업데이트
        with conn.cursor() as cursor:
            if file_path:  # 새 파일 업로드가 있는 경우 파일 경로 포함
                query = """
                UPDATE POST_TABLE
                SET POST_title = %s, POST_contents = %s, File_path = %s
                WHERE POST_id = %s
                """
                cursor.execute(query, (title, content, file_path, post_id))
            else:  # 파일 업로드가 없는 경우 파일 경로 제외
                query = """
                UPDATE POST_TABLE
                SET POST_title = %s, POST_contents = %s
                WHERE POST_id = %s
                """
                cursor.execute(query, (title, content, post_id))
            conn.commit()
        conn.close()
        flash('게시글 수정 완료', 'success')
        return redirect(url_for('index'))

    else:
        # GET 요청 시 기존 게시글 정보 가져오기
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM POST_TABLE WHERE POST_id = %s", (post_id,))
            post = cursor.fetchone()
        conn.close()
        return render_template('update_post.html', post=post)


# 게시글 삭제
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = db_connect()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM POST_TABLE WHERE POST_id = %s", (post_id,))
        conn.commit()
    conn.close()
    flash('게시글 삭제 완료', 'info')
    return redirect(url_for('index'))

# 게시글 검색
@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    게시글 검색.
    제목, 내용, 작성자 이름을 검색할 수 있으며 검색 결과를 메인 페이지에 표시.
    """
    query = request.args.get('query')  # 검색어
    search_type = request.args.get('type', 'all')  # 검색 범위: 제목, 내용, 작성자 이름 또는 전체

    conn = db_connect()
    with conn.cursor() as cursor:
        if search_type == 'title':
            cursor.execute("SELECT * FROM POST_TABLE WHERE POST_title LIKE CONCAT('%%', %s, '%%')", (query,))
        elif search_type == 'content':
            cursor.execute("SELECT * FROM POST_TABLE WHERE POST_contents LIKE CONCAT('%%', %s, '%%')", (query,))
        elif search_type == 'author':
            cursor.execute("""
                SELECT p.*, m.MEMBER_name 
                FROM POST_TABLE p
                JOIN MEMBERS m ON p.MEMBER_id = m.MEMBER_id
                WHERE m.MEMBER_name LIKE CONCAT('%%', %s, '%%')""", (query,))
        else:
            cursor.execute("""
                SELECT p.*, m.MEMBER_name 
                FROM POST_TABLE p
                JOIN MEMBERS m ON p.MEMBER_id = m.MEMBER_id
                WHERE p.POST_title LIKE CONCAT('%%', %s, '%%') 
                   OR p.POST_contents LIKE CONCAT('%%', %s, '%%') 
                   OR m.MEMBER_name LIKE CONCAT('%%', %s, '%%')""", (query, query, query))
        results = cursor.fetchall()
    conn.close()
    return render_template('index.html', posts=results, query=query, search_type=search_type)


# 앱 실행
if __name__ == '__main__':
    """
    애플리케이션 실행.
    Flask 서버는 0.0.0.0 호스트에서 5000번 포트로 실행되며 디버그 모드 활성화.
    """
    app.run(host='0.0.0.0', port=5000, debug=True)