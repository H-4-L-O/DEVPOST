-- init.sql

-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS DEVPOST;

-- 데이터베이스 사용
USE DEVPOST;

-- 회원 테이블 생성
CREATE TABLE IF NOT EXISTS MEMBERS (
    MEMBER_id INT AUTO_INCREMENT PRIMARY KEY, -- 회원 고유 ID
    MEMBER_name VARCHAR(10) NOT NULL,        -- 회원 이름
    School VARCHAR(30) NOT NULL,             -- 회원 학교
    User_email VARCHAR(100) NOT NULL UNIQUE, -- 회원 이메일
    User_id VARCHAR(50) NOT NULL UNIQUE,     -- 회원 ID
    User_password VARCHAR(255) NOT NULL,     -- 비밀번호
    USER_profile VARCHAR(255) DEFAULT NULL,  -- 프로필 이미지 파일 경로
    Create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 가입 날짜
);

-- 게시판 테이블 생성
CREATE TABLE IF NOT EXISTS POST_TABLE (
    POST_id INT AUTO_INCREMENT PRIMARY KEY, -- 게시판 고유 ID
    POST_title VARCHAR(50) NOT NULL, -- 게시판 제목
    POST_contents TEXT NOT NULL, -- 게시판 내용
    POST_password VARCHAR(255) DEFAULT NULL, -- 비밀글 비밀번호
    File_path VARCHAR(255) DEFAULT NULL, -- 첨부파일 경로
    MEMBER_id INT NOT NULL, -- 작성자 ID(외래키)
    Create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 게시판 생성 시간
    Update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 게시판 수정 시간
    CONSTRAINT MEMBER_id_fk FOREIGN KEY (MEMBER_id) REFERENCES MEMBERS(MEMBER_id)
    ON DELETE CASCADE -- 부모 행 삭제 시 자식 행도 삭제
    ON UPDATE CASCADE -- 부모 행 업데이트 시 자식 행도 업데이트
);