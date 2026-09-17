CREATE DATABASE IF NOT EXISTS transkrip_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE transkrip_db;

CREATE TABLE `user` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nik VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    role VARCHAR(20) NOT NULL,
    password_hash VARCHAR(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE transcript (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    uploaded_at DATETIME DEFAULT NULL,
    KEY user_id (user_id),
    CONSTRAINT transcript_ibfk_1 FOREIGN KEY (user_id) REFERENCES `user` (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
