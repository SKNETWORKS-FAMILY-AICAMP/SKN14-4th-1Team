-- Active: 1753716315111@@127.0.0.1@3306@nutriwisedb
-- pip install mysqlclient

-- # root 계정으로 접속

-- # 사용자 nutriwisedb/django 생성

create user 'django'@'%' identified by 'django';

-- # nutriwisedb 데이터베이스 생성
-- # - 인코딩 utf8mb4 (다국어/이모지 텍스트 지원 ver)
-- # - 정렬방식 utf8mb4_unicode_ci (대소문자 구분없음)
create database nutriwisedb character set utf8mb4 collate utf8mb4_unicode_ci;

-- # django 계정 권한 부여
grant all privileges on nutriwisedb.* to 'django'@'%';

flush privileges;

-- app > models.py 작업 후
-- python manage.py makemigrations uauth
-- python manage.py migrate uauth
-- python manage.py migrate

-- last_login 컬럼을 NULL 허용으로 변경
-- (기존에는 NOT NULL로 설정되어 있어, 로그인하지 않은 사용자도 last_login
ALTER TABLE auth_user MODIFY last_login DATETIME NULL;