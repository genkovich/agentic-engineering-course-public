-- Catalog BC.
CREATE TABLE IF NOT EXISTS catalog_categories (
    id   UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS catalog_products (
    id          UUID PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    price_cents BIGINT NOT NULL CHECK (price_cents >= 0),
    category_id UUID NOT NULL REFERENCES catalog_categories(id)
);

INSERT INTO catalog_categories (id, name) VALUES
    ('11111111-1111-1111-1111-111111111111', 'Books'),
    ('22222222-2222-2222-2222-222222222222', 'Electronics')
ON CONFLICT DO NOTHING;

INSERT INTO catalog_products (id, name, price_cents, category_id) VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'A Philosophy of Software Design', 4500, '11111111-1111-1111-1111-111111111111'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Domain-Driven Design', 6500, '11111111-1111-1111-1111-111111111111'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'Mechanical Keyboard', 18900, '22222222-2222-2222-2222-222222222222')
ON CONFLICT DO NOTHING;
