CREATE TABLE IF NOT EXISTS customers (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  tier VARCHAR(20) NOT NULL DEFAULT 'standard',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO customers (name, email, tier)
VALUES
  ('Alice Johnson', 'alice@example.com', 'gold'),
  ('Brian Lee', 'brian@example.com', 'standard'),
  ('Carla Gomez', 'carla@example.com', 'silver')
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  tier = VALUES(tier);
