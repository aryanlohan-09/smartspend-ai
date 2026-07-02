CREATE DATABASE IF NOT EXISTS smartspend_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'smartspend_user'@'%' IDENTIFIED BY 'smartspend_password';
GRANT ALL PRIVILEGES ON smartspend_ai.* TO 'smartspend_user'@'%';
FLUSH PRIVILEGES;
