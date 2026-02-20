-- users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_login ON users(login);

-- posts
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);