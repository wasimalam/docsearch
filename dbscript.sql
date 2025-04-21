CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash CHAR(60) NOT NULL, -- Length for bcrypt hash
    role INT DEFAULT 0, -- 0 for user, 1 for admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO users (username, email, password_hash)
VALUES ('admin', 'wasim@alamstech.net', '$2b$12$DQtL9YpUJjJwEYRi/.bLseiw082oPnbGn1EBoxqRaQvhfvYIglMBC');