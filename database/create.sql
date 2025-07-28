-- database/create.sql

-- 创建数据库（如果不存在）并切换
CREATE DATABASE IF NOT EXISTS polisage;
USE polisage;
SET GLOBAL time_zone = '+8:00';

-- 删除表（注意外键依赖顺序）
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS questions;

-- 创建文件表
CREATE TABLE IF NOT EXISTS files
(
    file_name   VARCHAR(255)           NOT NULL,
    file_type   ENUM ('json', 'image') NOT NULL,
    file_size   VARCHAR(28)            NOT NULL,
    upload_time DATETIME               NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (file_name)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;


CREATE TABLE IF NOT EXISTS questions
(
    questions_id  VARCHAR(16) NOT NULL,
    prev_id       VARCHAR(16) NULL,
    created_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    question_text TEXT        NOT NULL,
    answer_text   TEXT        NULL,
    reference     TEXT        NULL,
    feedback      TEXT        NULL,
    PRIMARY KEY (questions_id),
    INDEX idx_prev_id (prev_id),
    CONSTRAINT fk_prev_question
        FOREIGN KEY (prev_id)
            REFERENCES questions (questions_id)
            ON DELETE SET NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;
