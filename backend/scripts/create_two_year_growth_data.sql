-- Script to create 2 years of realistic invoice data showing business growth
-- Run this as: psql "postgresql://postgres:postgres@localhost:5432/manageros" -f backend/scripts/create_two_year_growth_data.sql

-- Disable RLS for this session (requires postgres superuser)
SET row_security = off;

-- Clear existing invoices to start fresh (optional - comment out if you want to keep existing data)
-- DELETE FROM invoices;

DO $$
DECLARE
    v_team_id INT;
    v_brand_id INT;
    v_campaign_id INT;
    v_invoice_num INT := 20000;
    v_month_date DATE;
    v_posting_date DATE;
    v_due_date DATE;
    v_amount DECIMAL(10,2);
    v_paid DECIMAL(10,2);
    v_customer TEXT;
    v_email TEXT;
    v_description TEXT;
    v_state TEXT;
    v_campaign_name TEXT;
    v_notes TEXT;

    -- Arrays for variety
    v_customers TEXT[] := ARRAY[
        'Acme Corporation', 'TechStart Inc.', 'Global Solutions Ltd',
        'Innovation Partners', 'Digital Ventures', 'Creative Studios',
        'Modern Brands Co', 'Enterprise Systems', 'Cloud Dynamics',
        'Next Gen Media', 'Velocity Partners', 'Horizon Technologies',
        'Pinnacle Group', 'Strategic Innovations', 'Synergy Solutions',
        'Apex Digital', 'Summit Ventures', 'Nexus Corp', 'Fusion Brands',
        'Catalyst Media', 'Momentum Group', 'Altitude Partners',
        'Emerge Technologies', 'Quantum Solutions', 'Elevate Brands'
    ];

    v_descriptions TEXT[] := ARRAY[
        'Social media content creation and management services',
        'Influencer marketing campaign for product launch',
        'Brand partnership and sponsored content production',
        'Multi-platform content creation and distribution',
        'Video production and post-production services',
        'Photography and creative direction for brand campaign',
        'Content strategy and execution for social channels',
        'Sponsored posts and story content across platforms',
        'Product review and unboxing content series',
        'Brand ambassador services and content creation',
        'Live streaming event coverage and promotion',
        'Tutorial and educational content production',
        'Behind-the-scenes content and brand storytelling',
        'Seasonal campaign content and creative assets',
        'Product launch promotion and awareness campaign',
        'User-generated content campaign management',
        'Influencer event coverage and activations',
        'Long-form video content series production',
        'TikTok viral challenge campaign execution',
        'Instagram Reels and Stories content package'
    ];

    v_month_count INT;
    v_invoices_this_month INT;
    v_base_amount DECIMAL(10,2);
    v_growth_factor DECIMAL(5,2);
    i INT;
    j INT;

BEGIN
    -- Get team and brand from existing data
    SELECT team_id, brand_id INTO v_team_id, v_brand_id
    FROM campaigns
    LIMIT 1;

    IF v_team_id IS NULL THEN
        RAISE NOTICE 'No campaigns found. Please create at least one campaign first.';
        RETURN;
    END IF;

    RAISE NOTICE 'Starting 2-year data generation for team % and brand %', v_team_id, v_brand_id;

    -- Generate data for 24 months (2 years ago to today)
    FOR v_month_count IN 0..23 LOOP
        -- Calculate the month date (going backwards from today)
        v_month_date := DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month' * (23 - v_month_count));

        -- Growth pattern: start with 3-5 invoices/month, grow to 12-18 invoices/month
        v_invoices_this_month := 3 + (v_month_count * 0.5)::INT + (RANDOM() * 3)::INT;

        -- Growth in average invoice amount: start at $1500, grow to $5000
        v_base_amount := 1500 + (v_month_count * 150);

        -- Create a campaign for this month (every 2-3 months)
        IF v_month_count % 2 = 0 OR v_month_count % 3 = 0 THEN
            v_campaign_name := 'Campaign ' || TO_CHAR(v_month_date, 'Mon YYYY') || ' - ' ||
                               v_customers[1 + (RANDOM() * (ARRAY_LENGTH(v_customers, 1) - 1))::INT];

            INSERT INTO campaigns (
                name,
                description,
                brand_id,
                team_id,
                state,
                created_at,
                updated_at
            ) VALUES (
                v_campaign_name,
                'Marketing campaign for ' || TO_CHAR(v_month_date, 'Month YYYY'),
                v_brand_id,
                v_team_id,
                CASE WHEN v_month_count < 20 THEN 'COMPLETED' ELSE 'ACTIVE' END,
                v_month_date,
                v_month_date
            ) RETURNING id INTO v_campaign_id;
        END IF;

        -- Generate invoices for this month
        FOR j IN 1..v_invoices_this_month LOOP
            -- Random posting date within the month
            v_posting_date := v_month_date + (RANDOM() * 28)::INT;

            -- Due date: 15-45 days after posting
            v_due_date := v_posting_date + (15 + (RANDOM() * 30)::INT);

            -- Amount: base amount + variation
            v_amount := v_base_amount + (RANDOM() * v_base_amount)::DECIMAL(10,2);

            -- Select customer
            v_customer := v_customers[1 + (RANDOM() * (ARRAY_LENGTH(v_customers, 1) - 1))::INT];
            v_email := LOWER(REPLACE(v_customer, ' ', '')) || '@example.com';

            -- Select description
            v_description := v_descriptions[1 + (RANDOM() * (ARRAY_LENGTH(v_descriptions, 1) - 1))::INT];

            -- Determine state and payment based on how old the invoice is
            IF v_due_date < CURRENT_DATE - INTERVAL '60 days' THEN
                -- Old invoices: mostly paid
                v_state := 'POSTED';
                IF RANDOM() > 0.15 THEN
                    -- 85% fully paid
                    v_paid := v_amount;
                ELSIF RANDOM() > 0.5 THEN
                    -- 7.5% partially paid
                    v_paid := v_amount * (0.3 + (RANDOM() * 0.6))::DECIMAL(10,2);
                ELSE
                    -- 7.5% unpaid (overdue)
                    v_paid := 0.00;
                END IF;
            ELSIF v_due_date < CURRENT_DATE - INTERVAL '30 days' THEN
                -- Recent past invoices: mix of paid/partial/unpaid
                v_state := 'POSTED';
                IF RANDOM() > 0.3 THEN
                    -- 70% fully paid
                    v_paid := v_amount;
                ELSIF RANDOM() > 0.5 THEN
                    -- 15% partially paid
                    v_paid := v_amount * (0.2 + (RANDOM() * 0.7))::DECIMAL(10,2);
                ELSE
                    -- 15% unpaid
                    v_paid := 0.00;
                END IF;
            ELSIF v_posting_date < CURRENT_DATE THEN
                -- Recently posted: mostly unpaid or partial
                v_state := 'POSTED';
                IF RANDOM() > 0.6 THEN
                    -- 40% fully paid
                    v_paid := v_amount;
                ELSIF RANDOM() > 0.5 THEN
                    -- 30% partially paid
                    v_paid := v_amount * (0.2 + (RANDOM() * 0.5))::DECIMAL(10,2);
                ELSE
                    -- 30% unpaid
                    v_paid := 0.00;
                END IF;
            ELSE
                -- Future dated: draft
                v_state := 'DRAFT';
                v_paid := 0.00;
            END IF;

            -- Add notes for some invoices
            IF RANDOM() > 0.7 THEN
                v_notes := (ARRAY[
                    'Payment terms: NET-30',
                    '50% deposit paid upfront',
                    'Final payment upon content delivery',
                    'Payment plan: 3 installments',
                    'Milestone-based payment structure',
                    'Includes usage rights and exclusivity',
                    'Early payment discount applied',
                    'Quarterly retainer invoice'
                ])[1 + (RANDOM() * 7)::INT];
            ELSE
                v_notes := NULL;
            END IF;

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
                notes,
                state,
                campaign_id,
                team_id,
                created_at,
                updated_at
            ) VALUES (
                v_invoice_num,
                v_customer,
                v_email,
                v_posting_date,
                v_due_date,
                v_amount,
                v_paid,
                v_description,
                v_notes,
                v_state,
                v_campaign_id,
                v_team_id,
                v_posting_date,
                v_posting_date
            );

            v_invoice_num := v_invoice_num + 1;
        END LOOP;

        RAISE NOTICE 'Month %: Created % invoices (avg amount: $%)',
                     TO_CHAR(v_month_date, 'Mon YYYY'),
                     v_invoices_this_month,
                     ROUND(v_base_amount, 2);
    END LOOP;

    RAISE NOTICE '✅ Completed! Generated 2 years of growth data.';
END $$;

-- Show summary statistics
SELECT
    '=== OVERALL SUMMARY ===' as section,
    COUNT(*) as total_invoices,
    TO_CHAR(SUM(amount_due), 'FM$999,999,990.00') as total_billed,
    TO_CHAR(SUM(amount_paid), 'FM$999,999,990.00') as total_collected,
    TO_CHAR(SUM(amount_due - amount_paid), 'FM$999,999,990.00') as total_outstanding,
    ROUND(100.0 * SUM(amount_paid) / NULLIF(SUM(amount_due), 0), 1) || '%' as collection_rate
FROM invoices;

-- Show growth by quarter
SELECT
    TO_CHAR(DATE_TRUNC('quarter', posting_date), 'YYYY-Q') as quarter,
    COUNT(*) as invoice_count,
    TO_CHAR(SUM(amount_due), 'FM$999,999,990.00') as total_billed,
    TO_CHAR(AVG(amount_due), 'FM$9,990.00') as avg_invoice_amount,
    TO_CHAR(SUM(amount_paid), 'FM$999,999,990.00') as total_collected,
    ROUND(100.0 * SUM(amount_paid) / NULLIF(SUM(amount_due), 0), 1) || '%' as collection_rate
FROM invoices
GROUP BY DATE_TRUNC('quarter', posting_date)
ORDER BY quarter;

-- Show state breakdown
SELECT
    state,
    COUNT(*) as count,
    TO_CHAR(SUM(amount_due), 'FM$999,999,990.00') as total_due,
    TO_CHAR(SUM(amount_paid), 'FM$999,999,990.00') as total_paid,
    TO_CHAR(SUM(amount_due - amount_paid), 'FM$999,999,990.00') as outstanding
FROM invoices
GROUP BY state
ORDER BY state;

-- Show monthly trend (last 12 months)
SELECT
    TO_CHAR(DATE_TRUNC('month', posting_date), 'YYYY-MM Mon') as month,
    COUNT(*) as invoices,
    TO_CHAR(SUM(amount_due), 'FM$999,990.00') as billed,
    TO_CHAR(AVG(amount_due), 'FM$9,990.00') as avg_amount
FROM invoices
WHERE posting_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', posting_date)
ORDER BY month;
