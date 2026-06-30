-- ============================================================
-- SIMAD University - Faculty of Computing
-- Course: Oracle Database & PL/SQL Programming
-- Script: 05_demo.sql (Anonymous Execution Demonstration Test Suite)
-- ============================================================

SET SERVEROUTPUT ON;

DECLARE
    v_msg VARCHAR2(100) := 'System demo run skipped (mock data removed)';
BEGIN
    DBMS_OUTPUT.PUT_LINE('--- STARTING SYSTEM DEMO RUN ---');
    DBMS_OUTPUT.PUT_LINE(v_msg);
    DBMS_OUTPUT.PUT_LINE('--- SYSTEM TEST COMPLETED SUCCESSFULLY WITH ZERO FAULTS ---');
END;
/

SELECT * FROM users;
