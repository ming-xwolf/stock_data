-- 设置 root 用户使用 mysql_native_password 认证方法（避免 caching_sha2_password 需要 TLS 的问题）
-- 注意：如果用户已存在，ALTER USER 会更新认证方法
ALTER USER IF EXISTS 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'test';

-- 创建允许从任何主机连接的用户
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'test';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;
