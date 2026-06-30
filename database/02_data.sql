-- ============================================================
-- SIMAD University - Faculty of Computing
-- Course: Oracle Database & PL/SQL Programming
-- Script: 02_data.sql (Sample Data & Admin Seed)
-- ============================================================

-- Create default primary administrator
INSERT INTO users (name, email, password, role) 
VALUES ('Admin Account', 'admin@gmail.com', 'admin123', 'admin');

COMMIT;
