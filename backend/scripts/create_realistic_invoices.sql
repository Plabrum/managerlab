-- Script to create realistic invoice data
-- Run this as: psql "postgresql://postgres:postgres@localhost:5432/manageros" -f backend/scripts/create_realistic_invoices.sql

-- Disable RLS for this session (requires postgres superuser)
SET row_security = off;

-- Get the first campaign ID
DO $$
DECLARE
    v_campaign_id INT;
    v_team_id INT;
    v_invoice_num INT := 10000;
    v_posting_date DATE;
    v_due_date DATE;
    v_amount DECIMAL(10,2);
    v_paid DECIMAL(10,2);
    v_customer TEXT;
    v_email TEXT;
    v_description TEXT;
    v_state TEXT;
    i INT;
BEGIN
    -- Get the first campaign and its team
    SELECT id, team_id INTO v_campaign_id, v_team_id FROM campaigns LIMIT 1;

    IF v_campaign_id IS NULL THEN
        RAISE NOTICE 'No campaigns found. Please create a campaign first.';
        RETURN;
    END IF;

    -- Create 10 realistic invoices with varying states
    FOR i IN 1..10 LOOP
        -- Vary the scenarios
        CASE (i % 5)
            WHEN 0 THEN
                -- Draft invoice
                v_posting_date := CURRENT_DATE;
                v_due_date := CURRENT_DATE + 30;
                v_amount := 1500.00 + (RANDOM() * 5000)::DECIMAL(10,2);
                v_paid := 0.00;
                v_state := 'DRAFT';
            WHEN 1 THEN
                -- Posted, recently sent, unpaid
                v_posting_date := CURRENT_DATE - (RANDOM() * 7)::INT;
                v_due_date := CURRENT_DATE + (15 + (RANDOM() * 15)::INT);
                v_amount := 2000.00 + (RANDOM() * 8000)::DECIMAL(10,2);
                v_paid := 0.00;
                v_state := 'POSTED';
            WHEN 2 THEN
                -- Posted, partially paid
                v_posting_date := CURRENT_DATE - (10 + (RANDOM() * 20)::INT);
                v_due_date := CURRENT_DATE + (5 + (RANDOM() * 15)::INT);
                v_amount := 3000.00 + (RANDOM() * 7000)::DECIMAL(10,2);
                v_paid := v_amount * (0.3 + (RANDOM() * 0.4))::DECIMAL(10,2);
                v_state := 'POSTED';
            WHEN 3 THEN
                -- Posted, fully paid
                v_posting_date := CURRENT_DATE - (30 + (RANDOM() * 60)::INT);
                v_due_date := CURRENT_DATE + ((RANDOM() * 20)::INT - 10);
                v_amount := 5000.00 + (RANDOM() * 10000)::DECIMAL(10,2);
                v_paid := v_amount;
                v_state := 'POSTED';
            ELSE
                -- Posted, overdue, unpaid or partially paid
                v_posting_date := CURRENT_DATE - (45 + (RANDOM() * 45)::INT);
                v_due_date := CURRENT_DATE - (1 + (RANDOM() * 30)::INT);
                v_amount := 2500.00 + (RANDOM() * 7500)::DECIMAL(10,2);
                v_paid := CASE WHEN RANDOM() > 0.5 THEN 0.00 ELSE v_amount * (RANDOM() * 0.5)::DECIMAL(10,2) END;
                v_state := 'POSTED';
        END CASE;

        -- Generate customer info
        v_customer := (ARRAY['Acme Corporation', 'TechStart Inc.', 'Global Solutions Ltd',
                             'Innovation Partners', 'Digital Ventures', 'Creative Studios',
                             'Modern Brands Co', 'Enterprise Systems', 'Cloud Dynamics',
                             'Next Gen Media'])[1 + (RANDOM() * 9)::INT];
        v_email := LOWER(REPLACE(v_customer, ' ', '')) || '@example.com';

        -- Generate description
        v_description := (ARRAY[
            'Social media content creation and management services',
            'Influencer marketing campaign for Q4 product launch',
            'Brand partnership and sponsored content production',
            'Multi-platform content creation and distribution',
            'Video production and post-production services',
            'Photography and creative direction for brand campaign',
            'Content strategy and execution for social channels',
            'Sponsored posts and story content across platforms',
            'Product review and unboxing content series',
            'Brand ambassador services and content creation'
        ])[1 + (RANDOM() * 9)::INT];

        -- Insert invoice
        INSERT INTO invoices (
            invoice_number,
            customer_name,
            customer_email,
            posting_date,
            due_date,
            amount_due,
            amount_paid,
            description,
            state,
            campaign_id,
            team_id,
            created_at,
            updated_at
        ) VALUES (
            v_invoice_num + i,
            v_customer,
            v_email,
            v_posting_date,
            v_due_date,
            v_amount,
            v_paid,
            v_description,
            v_state,
            v_campaign_id,
            v_team_id,
            NOW(),
            NOW()
        );
    END LOOP;

    RAISE NOTICE 'Created 10 realistic invoices for campaign %', v_campaign_id;
END $$;

-- Show summary
SELECT
    state,
    COUNT(*) as count,
    SUM(amount_due) as total_due,
    SUM(amount_paid) as total_paid,
    SUM(amount_due - amount_paid) as outstanding
FROM invoices
GROUP BY state
ORDER BY state;
