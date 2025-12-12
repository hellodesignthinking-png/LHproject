-- ZeroSite v24 PostgreSQL Schema
-- Phase 7.1: Database Design for 13 Engines

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    land_area_sqm FLOAT NOT NULL,
    zoning_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analyses table
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id),
    analysis_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    results JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Engine results (13 engines)
CREATE TABLE engine_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analyses(id),
    engine_name VARCHAR(50),
    engine_version VARCHAR(20),
    input_data JSONB,
    output_data JSONB,
    execution_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analyses(id),
    report_type VARCHAR(50),
    format VARCHAR(10),
    file_path VARCHAR(500),
    file_size_kb INT,
    page_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Visualizations table
CREATE TABLE visualizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analyses(id),
    viz_type VARCHAR(50),
    format VARCHAR(10),
    file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table (for authentication)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_projects_location ON projects(location);
CREATE INDEX idx_analyses_project_id ON analyses(project_id);
CREATE INDEX idx_engine_results_analysis_id ON engine_results(analysis_id);
CREATE INDEX idx_reports_analysis_id ON reports(analysis_id);
CREATE INDEX idx_visualizations_analysis_id ON visualizations(analysis_id);

-- Sample data
INSERT INTO projects (name, location, land_area_sqm, zoning_type) VALUES
('Test Project 1', 'Seoul', 660.0, '제2종일반주거지역'),
('Test Project 2', 'Busan', 1200.0, '준주거지역');

COMMENT ON TABLE projects IS 'Main projects table storing site information';
COMMENT ON TABLE analyses IS 'Analysis records with results from 13 engines';
COMMENT ON TABLE engine_results IS 'Detailed results from each engine execution';
COMMENT ON TABLE reports IS 'Generated reports (LH, landowner, professional, etc)';
COMMENT ON TABLE visualizations IS 'Generated charts and visualizations';
