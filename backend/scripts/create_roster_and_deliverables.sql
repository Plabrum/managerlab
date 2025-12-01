-- Script to create roster members and deliverables showing 2-year growth
-- Run this as: psql "postgresql://postgres:postgres@localhost:5432/manageros" -f backend/scripts/create_roster_and_deliverables.sql

-- Disable RLS for this session (requires postgres superuser)
SET row_security = off;

DO $$
DECLARE
    v_team_id INT;
    v_user_id INT;
    v_roster_ids INT[];
    v_roster_id INT;
    v_campaign_ids INT[];
    v_campaign_id INT;
    v_month_date DATE;
    v_posting_date TIMESTAMP;
    v_deliverable_title TEXT;
    v_deliverable_content TEXT;
    v_platform TEXT;
    v_deliverable_type TEXT;
    v_state TEXT;
    v_count INT;

    -- Arrays for variety
    v_roster_names TEXT[] := ARRAY[
        'Emma Rodriguez', 'James Chen', 'Sofia Martinez', 'Michael Johnson',
        'Isabella Garcia', 'Alexander Kim', 'Olivia Thompson', 'Daniel Lee',
        'Mia Anderson', 'William Zhang', 'Charlotte Wilson', 'David Park',
        'Amelia Brown', 'Joseph Taylor', 'Harper Davis', 'Christopher Moore',
        'Evelyn Martinez', 'Matthew Robinson', 'Abigail White', 'Joshua Harris'
    ];

    v_instagram_handles TEXT[] := ARRAY[
        '@emmalifestyle', '@jamestech', '@sofiafitness', '@michaelcooks',
        '@isabellafashion', '@alexgaming', '@oliviabeauty', '@danieltravel',
        '@miahealth', '@williamfinance', '@charlotteart', '@davidfood',
        '@ameliamusic', '@josephsports', '@harperhome', '@chrisphotography',
        '@evelynstyle', '@matthewfitness', '@abigailwellness', '@joshuatech'
    ];

    v_tiktok_handles TEXT[] := ARRAY[
        '@emmalifetok', '@jamestechie', '@sofiafitt', '@mikecookss',
        '@belafashion', '@alexgames', '@livbeauty', '@dantravels',
        '@miahealthy', '@willmoney', '@charliearts', '@davefoodie',
        '@amelmusic', '@joesporty', '@harperhomee', '@chrisphoto',
        '@evestyle', '@mattfit', '@abiwellness', '@joshtech'
    ];

    v_platforms TEXT[] := ARRAY['INSTAGRAM', 'TIKTOK', 'YOUTUBE', 'FACEBOOK'];

    v_deliverable_types TEXT[] := ARRAY[
        'INSTAGRAM_FEED_POST', 'INSTAGRAM_STORY_FRAME', 'INSTAGRAM_REEL', 'INSTAGRAM_CAROUSEL',
        'TIKTOK_VIDEO', 'TIKTOK_PHOTO_POST',
        'YOUTUBE_VIDEO', 'YOUTUBE_SHORT',
        'FACEBOOK_POST', 'FACEBOOK_REEL'
    ];

    v_title_templates TEXT[] := ARRAY[
        'Product Review: %s',
        'Unboxing & First Impressions',
        'Day in the Life with %s',
        'Tutorial: How to Use %s',
        'Styling Tips featuring %s',
        'Behind the Scenes Content',
        'Get Ready With Me ft. %s',
        'Product Haul & Try-On',
        '24 Hour Challenge with %s',
        'Honest Review: %s',
        'Morning Routine featuring %s',
        'Favorite Products of the Month',
        'Brand Partnership Announcement',
        'Giveaway & Contest Post',
        'Q&A Session with %s'
    ];

    v_brand_names TEXT[] := ARRAY[
        'Brand X', 'ProductCo', 'BeautyBrand', 'TechGear',
        'FitnessLife', 'FashionHub', 'HomeGoods', 'WellnessPlus'
    ];

    v_month_count INT;
    v_deliverables_this_month INT;
    v_roster_idx INT;
    i INT;
    j INT;

BEGIN
    -- Get team and user IDs
    SELECT team_id INTO v_team_id FROM campaigns LIMIT 1;
    SELECT id INTO v_user_id FROM users LIMIT 1;

    IF v_team_id IS NULL OR v_user_id IS NULL THEN
        RAISE NOTICE 'Missing team or user. Please ensure data exists.';
        RETURN;
    END IF;

    RAISE NOTICE '=== STEP 1: Creating Roster Members ===';

    -- Create 20 roster members (influencers/talent)
    v_roster_ids := ARRAY[]::INT[];

    FOR i IN 1..20 LOOP
        INSERT INTO roster (
            user_id,
            team_id,
            name,
            email,
            instagram_handle,
            tiktok_handle,
            youtube_channel,
            state,
            created_at,
            updated_at
        ) VALUES (
            v_user_id,
            v_team_id,
            v_roster_names[i],
            LOWER(REPLACE(v_roster_names[i], ' ', '.')) || '@example.com',
            v_instagram_handles[i],
            v_tiktok_handles[i],
            REPLACE(v_roster_names[i], ' ', '') || 'Official',
            'ACTIVE',
            CURRENT_DATE - INTERVAL '2 years',
            CURRENT_DATE
        ) RETURNING id INTO v_roster_id;

        v_roster_ids := array_append(v_roster_ids, v_roster_id);

        IF i <= 5 THEN
            RAISE NOTICE 'Created roster: % (ID: %)', v_roster_names[i], v_roster_id;
        END IF;
    END LOOP;

    RAISE NOTICE 'Created % roster members total', array_length(v_roster_ids, 1);

    RAISE NOTICE '';
    RAISE NOTICE '=== STEP 2: Assigning Roster to Campaigns ===';

    -- Get all campaign IDs
    SELECT ARRAY_AGG(id) INTO v_campaign_ids FROM campaigns WHERE team_id = v_team_id;

    -- Assign roster members to campaigns (each campaign gets 1 roster member)
    FOR i IN 1..array_length(v_campaign_ids, 1) LOOP
        -- Rotate through roster members
        v_roster_idx := ((i - 1) % array_length(v_roster_ids, 1)) + 1;
        v_roster_id := v_roster_ids[v_roster_idx];

        UPDATE campaigns
        SET assigned_roster_id = v_roster_id
        WHERE id = v_campaign_ids[i];
    END LOOP;

    RAISE NOTICE 'Assigned roster members to % campaigns', array_length(v_campaign_ids, 1);

    RAISE NOTICE '';
    RAISE NOTICE '=== STEP 3: Creating Deliverables (2-year growth) ===';

    -- Generate deliverables for 24 months showing growth
    FOR v_month_count IN 0..23 LOOP
        -- Calculate the month date (going backwards from today)
        v_month_date := DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month' * (23 - v_month_count));

        -- Growth pattern: start with 8-12 deliverables/month, grow to 30-40 deliverables/month
        v_deliverables_this_month := 8 + (v_month_count * 1.2)::INT + (RANDOM() * 5)::INT;

        -- Create deliverables for this month
        FOR j IN 1..v_deliverables_this_month LOOP
            -- Select a random campaign from this period
            v_campaign_id := v_campaign_ids[1 + (RANDOM() * (array_length(v_campaign_ids, 1) - 1))::INT];

            -- Random posting date within the month
            v_posting_date := v_month_date + (RANDOM() * 28)::INT +
                             INTERVAL '1 hour' * (RANDOM() * 24)::INT;

            -- Select platform (weighted towards Instagram and TikTok)
            IF RANDOM() < 0.4 THEN
                v_platform := 'INSTAGRAM';
                v_deliverable_type := (ARRAY['INSTAGRAM_FEED_POST', 'INSTAGRAM_STORY_FRAME',
                                             'INSTAGRAM_REEL', 'INSTAGRAM_CAROUSEL'])
                                      [1 + (RANDOM() * 3)::INT];
            ELSIF RANDOM() < 0.7 THEN
                v_platform := 'TIKTOK';
                v_deliverable_type := (ARRAY['TIKTOK_VIDEO', 'TIKTOK_PHOTO_POST'])
                                      [1 + (RANDOM() * 1)::INT];
            ELSIF RANDOM() < 0.85 THEN
                v_platform := 'YOUTUBE';
                v_deliverable_type := (ARRAY['YOUTUBE_VIDEO', 'YOUTUBE_SHORT'])
                                      [1 + (RANDOM() * 1)::INT];
            ELSE
                v_platform := 'FACEBOOK';
                v_deliverable_type := (ARRAY['FACEBOOK_POST', 'FACEBOOK_REEL'])
                                      [1 + (RANDOM() * 1)::INT];
            END IF;

            -- Generate title
            v_deliverable_title := FORMAT(
                v_title_templates[1 + (RANDOM() * (array_length(v_title_templates, 1) - 1))::INT],
                v_brand_names[1 + (RANDOM() * (array_length(v_brand_names, 1) - 1))::INT]
            );

            -- Generate content/caption
            v_deliverable_content := 'Excited to share this amazing collaboration! ' ||
                                    CASE
                                        WHEN RANDOM() > 0.5 THEN 'Check out my latest post featuring this incredible product. '
                                        ELSE 'So grateful for this partnership. '
                                    END ||
                                    'Link in bio for more details! #ad #sponsored #partner';

            -- Determine state based on posting date
            IF v_posting_date < CURRENT_TIMESTAMP - INTERVAL '7 days' THEN
                -- Old deliverables: mostly posted
                IF RANDOM() > 0.1 THEN
                    v_state := 'POSTED';
                ELSIF RANDOM() > 0.5 THEN
                    v_state := 'APPROVED';
                ELSE
                    v_state := 'IN_REVIEW';
                END IF;
            ELSIF v_posting_date < CURRENT_TIMESTAMP THEN
                -- Recent deliverables: mix of states
                IF RANDOM() > 0.4 THEN
                    v_state := 'POSTED';
                ELSIF RANDOM() > 0.5 THEN
                    v_state := 'APPROVED';
                ELSE
                    v_state := 'IN_REVIEW';
                END IF;
            ELSE
                -- Future deliverables: draft or in review
                IF RANDOM() > 0.6 THEN
                    v_state := 'DRAFT';
                ELSIF RANDOM() > 0.5 THEN
                    v_state := 'IN_REVIEW';
                ELSE
                    v_state := 'APPROVED';
                END IF;
            END IF;

            -- Count (usually 1, sometimes 2-3 for story frames)
            IF v_deliverable_type LIKE '%STORY%' THEN
                v_count := 1 + (RANDOM() * 2)::INT;
            ELSE
                v_count := 1;
            END IF;

            -- Insert deliverable
            INSERT INTO deliverables (
                title,
                content,
                platforms,
                deliverable_type,
                count,
                posting_date,
                posting_start_date,
                posting_end_date,
                handles,
                hashtags,
                disclosures,
                approval_required,
                state,
                campaign_id,
                team_id,
                created_at,
                updated_at
            ) VALUES (
                v_deliverable_title,
                v_deliverable_content,
                v_platform::socialmediaplatforms,
                v_deliverable_type::deliverabletype,
                v_count,
                v_posting_date,
                v_posting_date::DATE,
                (v_posting_date + INTERVAL '1 day')::DATE,
                ARRAY['@brandhandle', '@partnerhandle'],
                ARRAY['#ad', '#sponsored', '#partner', '#collab'],
                ARRAY['#ad', '#sponsored'],
                TRUE,
                v_state,
                v_campaign_id,
                v_team_id,
                v_posting_date - INTERVAL '7 days',
                v_posting_date - INTERVAL '7 days'
            );
        END LOOP;

        IF v_month_count % 3 = 0 THEN
            RAISE NOTICE 'Month %: Created % deliverables',
                         TO_CHAR(v_month_date, 'Mon YYYY'),
                         v_deliverables_this_month;
        END IF;
    END LOOP;

    RAISE NOTICE '';
    RAISE NOTICE '✅ Completed! Generated roster members and deliverables.';
END $$;

-- Show summary statistics
SELECT '=== ROSTER SUMMARY ===' as section;
SELECT
    state,
    COUNT(*) as count,
    STRING_AGG(DISTINCT name, ', ') as sample_names
FROM roster
GROUP BY state
ORDER BY state;

SELECT '';
SELECT '=== DELIVERABLES SUMMARY ===' as section;
SELECT
    state,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) || '%' as percentage
FROM deliverables
GROUP BY state
ORDER BY
    CASE state
        WHEN 'POSTED' THEN 1
        WHEN 'APPROVED' THEN 2
        WHEN 'IN_REVIEW' THEN 3
        WHEN 'DRAFT' THEN 4
    END;

SELECT '';
SELECT '=== DELIVERABLES BY PLATFORM ===' as section;
SELECT
    platforms,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) || '%' as percentage
FROM deliverables
GROUP BY platforms
ORDER BY count DESC;

SELECT '';
SELECT '=== QUARTERLY GROWTH ===' as section;
SELECT
    TO_CHAR(DATE_TRUNC('quarter', posting_date), 'YYYY-Q') as quarter,
    COUNT(*) as deliverable_count,
    COUNT(DISTINCT campaign_id) as campaigns_with_deliverables,
    ROUND(AVG(count), 1) as avg_count_per_deliverable
FROM deliverables
GROUP BY DATE_TRUNC('quarter', posting_date)
ORDER BY quarter;

SELECT '';
SELECT '=== MONTHLY TREND (Last 12 months) ===' as section;
SELECT
    TO_CHAR(DATE_TRUNC('month', posting_date), 'YYYY-MM Mon') as month,
    COUNT(*) as deliverables,
    COUNT(CASE WHEN state = 'POSTED' THEN 1 END) as posted,
    COUNT(CASE WHEN platforms = 'INSTAGRAM' THEN 1 END) as instagram,
    COUNT(CASE WHEN platforms = 'TIKTOK' THEN 1 END) as tiktok
FROM deliverables
WHERE posting_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', posting_date)
ORDER BY month;

SELECT '';
SELECT '=== TOP PERFORMING ROSTER (by deliverable count) ===' as section;
SELECT
    r.name,
    r.instagram_handle,
    COUNT(d.id) as total_deliverables,
    COUNT(CASE WHEN d.state = 'POSTED' THEN 1 END) as posted,
    COUNT(CASE WHEN d.platforms = 'INSTAGRAM' THEN 1 END) as instagram,
    COUNT(CASE WHEN d.platforms = 'TIKTOK' THEN 1 END) as tiktok
FROM roster r
JOIN campaigns c ON c.assigned_roster_id = r.id
JOIN deliverables d ON d.campaign_id = c.id
GROUP BY r.id, r.name, r.instagram_handle
ORDER BY total_deliverables DESC
LIMIT 10;
