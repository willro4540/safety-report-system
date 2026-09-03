-- 시설 안전 민원 신고 프로그램 — v2 MySQL 스키마
-- 이 파일은 db/connection.py의 Mock(로컬 JSON 폴백)을 걷어내고
-- 실제 MySQL 연동으로 넘어갈 때 기준이 되는 테이블 정의입니다.
-- 문자셋: utf8mb4 (한글 + 이모지 상태 아이콘 대비)

CREATE DATABASE IF NOT EXISTS safety_report
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE safety_report;

-- 회원(신고자/관리자 공통)
CREATE TABLE users (
    user_id     VARCHAR(20)  PRIMARY KEY,
    password    VARCHAR(60)  NOT NULL,   -- bcrypt 해시 고정 길이(60자)
    name        VARCHAR(50)  NOT NULL,
    phone       VARCHAR(20)  NOT NULL,
    role        ENUM('user','admin') NOT NULL DEFAULT 'user',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARACTER SET utf8mb4;

-- 민원 신고 (구 SQL의 `complaints` → `reports`로 통일, 2026-09-03 결정)
CREATE TABLE reports (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        VARCHAR(20)  NOT NULL,
    type           VARCHAR(30)  NOT NULL,
    location       VARCHAR(255) NOT NULL,   -- 사람이 읽는 주소/설명 텍스트
    latitude       DOUBLE       NULL,       -- EPSG:4326(WGS84), GPS EXIF 원본값 그대로
    longitude      DOUBLE       NULL,       -- EPSG:4326(WGS84)
    content        TEXT         NOT NULL,
    image_path     VARCHAR(255) NULL,
    status         ENUM('접수','처리중','완료','기각') NOT NULL DEFAULT '접수',
    reject_reason  TEXT         NULL,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB CHARACTER SET utf8mb4;

-- 관리자 처리 이력 (감사 로그) — 누가/언제/어떤 신고에 무슨 처분을 내렸는지
CREATE TABLE admin_actions (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    report_id    INT          NOT NULL,
    admin_id     VARCHAR(20)  NOT NULL,
    action       ENUM('완료처리','기각') NOT NULL,
    reason       TEXT         NULL,        -- 기각 사유(완료처리 시엔 NULL)
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id),
    FOREIGN KEY (admin_id)  REFERENCES users(user_id)
) ENGINE=InnoDB CHARACTER SET utf8mb4;
