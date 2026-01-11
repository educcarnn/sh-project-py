SELECT
    u.name        AS user_name,
    u.email       AS user_email,
    r.description AS role_description,
    c.description AS claim_description
FROM users u
INNER JOIN roles r
    ON u.role_id = r.id
LEFT JOIN user_claims uc
    ON uc.user_id = u.id
LEFT JOIN claims c
    ON c.id = uc.claim_id;
