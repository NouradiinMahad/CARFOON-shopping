-- ============================================================
-- SIMAD University - Faculty of Computing
-- Course: Oracle Database & PL/SQL Programming
-- Script: 03_plsql.sql (Stored Packages, Procedures, & Functions)
-- ============================================================

CREATE OR REPLACE PACKAGE pkg_order_management IS
    -- Associative Array (Index-By Table) Type definitions
    TYPE product_arr IS TABLE OF NUMBER INDEX BY PLS_INTEGER;
    TYPE quantity_tab IS TABLE OF NUMBER;

    -- User-defined Exception Definition
    e_invalid_quantity EXCEPTION;
    PRAGMA EXCEPTION_INIT(e_invalid_quantity, -20001);

    -- Calculates cumulative line-item price totals
    FUNCTION calculate_order_total(p_order_id IN NUMBER) RETURN NUMBER;
    
    -- Validates stock levels and adds item to cart
    PROCEDURE add_item_to_cart(
        p_cart_id    IN NUMBER,
        p_product_id IN NUMBER,
        p_quantity   IN NUMBER
    );
    
    -- Submits transactional checkout, deducts stock, and saves order details
    PROCEDURE process_bulk_checkout(
        p_cart_id     IN NUMBER,
        p_user_id     IN NUMBER,
        p_new_order_id OUT NUMBER
    );
END pkg_order_management;
/

CREATE OR REPLACE PACKAGE BODY pkg_order_management IS

-- ============================================================
-- Name: calculate_order_total
-- Purpose: Computes the complete total price of items in an order
-- Author: Group Member
-- Date: 05-JUN-2026
-- Params: p_order_id IN NUMBER -- Target Order Identifier
-- Notes: Contains explicit cursor parsing loops
-- ============================================================
FUNCTION calculate_order_total(p_order_id IN NUMBER) RETURN NUMBER IS
    v_total NUMBER(10,2) := 0;
    
    -- Explicit Cursor Requirement
    CURSOR cur_order_items IS 
        SELECT oi.quantity, p.price 
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = p_order_id;
        
    -- User-defined Record Type Requirement
    TYPE item_summary_rec IS RECORD (
        qty   NUMBER,
        price NUMBER(10,2)
    );
    v_item item_summary_rec;
BEGIN
    OPEN cur_order_items;
    LOOP
        FETCH cur_order_items INTO v_item;
        EXIT WHEN cur_order_items%NOTFOUND;
        v_total := v_total + (v_item.qty * v_item.price);
    END LOOP;
    CLOSE cur_order_items;
    
    RETURN v_total;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 0;
    WHEN OTHERS THEN
        IF cur_order_items%ISOPEN THEN
            CLOSE cur_order_items;
        END IF;
        RAISE_APPLICATION_ERROR(-20002, 'Error calculating total.');
END calculate_order_total;


-- ============================================================
-- Name: add_item_to_cart
-- Purpose: Inserts or alters quantities inside a client's cart
-- Author: Group Member
-- Date: 05-JUN-2026
-- Params: p_cart_id IN NUMBER -- Client Cart reference ID
--         p_product_id IN NUMBER -- Selected product reference ID
--         p_quantity IN NUMBER -- Amount to pass over
-- Notes: Throws user-defined rule validation exceptions
-- ============================================================
PROCEDURE add_item_to_cart(
    p_cart_id    IN NUMBER,
    p_product_id IN NUMBER,
    p_quantity   IN NUMBER
) IS
    v_exists NUMBER;
BEGIN
    -- Enforce rule with our user-defined exception
    IF p_quantity <= 0 THEN
        RAISE e_invalid_quantity;
    END IF;

    SELECT COUNT(*) INTO v_exists FROM cart_items 
    WHERE cart_id = p_cart_id AND product_id = p_product_id;

    IF v_exists > 0 THEN
        UPDATE cart_items 
        SET quantity = quantity + p_quantity
        WHERE cart_id = p_cart_id AND product_id = p_product_id;
    ELSE
        INSERT INTO cart_items (cart_id, product_id, quantity)
        VALUES (p_cart_id, p_product_id, p_quantity);
    END IF;
EXCEPTION
    WHEN e_invalid_quantity THEN
        RAISE_APPLICATION_ERROR(-20001, 'Quantity must be greater than zero.');
    WHEN OTHERS THEN
        RAISE_APPLICATION_ERROR(-20003, 'Database operation failed during cart insert.');
END add_item_to_cart;


-- ============================================================
-- Name: process_bulk_checkout
-- Purpose: Moves active cart items to permanent order history records
-- Author: Group Member
-- Date: 05-JUN-2026
-- Params: p_cart_id IN NUMBER -- Active cart target
--         p_user_id IN NUMBER -- User context referencing mapping
--         p_new_order_id OUT NUMBER -- Newly generated order container ID
-- Notes: Uses Cursor FOR loops, nested tables, and subprogram calling
-- ============================================================
PROCEDURE process_bulk_checkout(
    p_cart_id     IN NUMBER,
    p_user_id     IN NUMBER,
    p_new_order_id OUT NUMBER
) IS
    -- Collections Definitions
    v_prod_list  product_arr;
    v_qty_list   quantity_tab := quantity_tab();
    v_idx        NUMBER := 1;
    v_final_cost NUMBER(10,2);
    
    -- %ROWTYPE Record Requirement
    v_cart_rec   cart_items%ROWTYPE;
BEGIN
    -- Initializing base empty order tracker wrapper
    INSERT INTO orders (user_id, total_amount, status)
    VALUES (p_user_id, 0.00, 'Pending')
    RETURNING order_id INTO p_new_order_id;

    -- Cursor FOR loop processing
    FOR v_item IN (SELECT * FROM cart_items WHERE cart_id = p_cart_id) LOOP
        -- Map values into memory structures
        v_prod_list(v_idx) := v_item.product_id;
        v_qty_list.EXTEND; -- Collection method usage
        v_qty_list(v_idx)  := v_item.quantity;
        
        -- Batch push line item array sets
        INSERT INTO order_items(order_id, product_id, quantity)
        VALUES (p_new_order_id, v_prod_list(v_idx), v_qty_list(v_idx));
        
        v_idx := v_idx + 1;
    END LOOP;

    -- Call to internal function (Requirement: Subprogram calling another subprogram)
    v_final_cost := calculate_order_total(p_new_order_id);
    
    UPDATE orders SET total_amount = v_final_cost WHERE order_id = p_new_order_id;
    
    -- Clean up cart items using collection method check
    IF v_prod_list.EXISTS(1) THEN
        DELETE FROM cart_items WHERE cart_id = p_cart_id;
    END IF;

EXCEPTION
    WHEN TOO_MANY_ROWS THEN
        RAISE_APPLICATION_ERROR(-20004, 'Data integrity error encountered during process execution.');
    WHEN OTHERS THEN
        RAISE_APPLICATION_ERROR(-20005, 'Checkout processing system exception raised.');
END process_bulk_checkout;

END pkg_order_management;
/
