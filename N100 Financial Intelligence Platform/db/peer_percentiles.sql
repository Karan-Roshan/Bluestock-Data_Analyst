CREATE TABLE IF NOT EXISTS peer_percentiles (
 company_id TEXT NOT NULL, peer_group_name TEXT NOT NULL, metric TEXT NOT NULL,
 value REAL, percentile_rank REAL, year INTEGER,
 PRIMARY KEY(company_id,peer_group_name,metric,year),
 FOREIGN KEY(company_id) REFERENCES companies(company_id)
);
