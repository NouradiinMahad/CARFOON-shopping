-- ============================================================
-- SIMAD University - Faculty of Computing
-- Course: Oracle Database & PL/SQL Programming
-- Script: 04_triggers.sql (Database Triggers)
-- ============================================================

-- ============================================================
-- Name: trg_products_before_insert
-- Purpose: Ensures product names are properly uppercase for formatting consistency
-- Table: products
-- Event: BEFORE INSERT
-- ============================================================
CREATE OR REPLACE TRIGGER trg_products_before_insert
BEFORE INSERT ON products
FOR EACH ROW
BEGIN
    :new.name := UPPER(:new.name);
END;
/


-- ============================================================
-- Name: trg_orders_after_update
-- Purpose: Logs order updates to the audit log table for visibility tracking
-- Table: orders
-- Event: AFTER UPDATE
-- ============================================================
CREATE OR REPLACE TRIGGER trg_orders_after_update
AFTER UPDATE OF status ON orders
FOR EACH ROW
BEGIN
    INSERT INTO order_audit_logs (order_id, old_status, new_status)
    VALUES (:old.order_id, :old.status, :new.status);
END;
/


-- ============================================================
-- Name: trg_update_stock
-- Purpose: Automatically updates product stock after an order item is added
-- Table: order_items
-- Event: AFTER INSERT
-- ============================================================
CREATE OR REPLACE TRIGGER trg_update_stock
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET stock_quantity = stock_quantity - :new.quantity
    WHERE product_id = :new.product_id;
END;
/


-- ============================================================
-- Name: trg_system_audit
-- Purpose: Logs important system activities on products table
-- Table: products
-- Event: AFTER INSERT OR UPDATE OR DELETE
-- ============================================================
CREATE OR REPLACE TRIGGER trg_system_audit
AFTER INSERT OR UPDATE OR DELETE ON products
FOR EACH ROW
DECLARE
    v_action VARCHAR2(20);
    v_product_id NUMBER;
BEGIN
    IF INSERTING THEN
        v_action := 'INSERT';
        v_product_id := :new.product_id;
    ELSIF UPDATING THEN
        v_action := 'UPDATE';
        v_product_id := :new.product_id;
    ELSIF DELETING THEN
        v_action := 'DELETE';
        v_product_id := :old.product_id;
    END IF;

    -- Generic system activity logging
    INSERT INTO order_audit_logs (order_id, old_status, new_status)
    VALUES (v_product_id, v_action, 'PRODUCT_TABLE');
END;
/
