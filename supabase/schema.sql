-- Supabase schema for EII

CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    source TEXT,
    url TEXT,
    author TEXT,
    content TEXT,
    published_at TIMESTAMP,
    scored_at TIMESTAMP
);

CREATE TABLE scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id),
    confidence INT,
    jargon_density INT,
    self_reference INT,
    originality INT,
    humor_rating INT,
    summary TEXT
);