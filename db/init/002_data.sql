USE mcp_demo;

INSERT INTO users (full_name, department, email, location) VALUES
('Alice Carter', 'Finance', 'alice.carter@example.local', 'London'),
('Ben Morris', 'IT', 'ben.morris@example.local', 'Manchester'),
('Chloe Singh', 'HR', 'chloe.singh@example.local', 'Birmingham'),
('Daniel Reed', 'Sales', 'daniel.reed@example.local', 'London'),
('Emma Hughes', 'Operations', 'emma.hughes@example.local', 'Leeds');

INSERT INTO assets (asset_tag, asset_type, manufacturer, model, serial_number, assigned_user_id, purchase_date, warranty_expiry, status) VALUES
('LAP-1001', 'Laptop', 'Dell', 'Latitude 7440', 'SN-DEL-7440-001', 1, '2024-02-10', '2027-02-10', 'In Use'),
('LAP-1002', 'Laptop', 'Lenovo', 'ThinkPad T14', 'SN-LEN-T14-002', 2, '2023-11-05', '2026-11-05', 'In Use'),
('PHN-2001', 'Phone', 'Apple', 'iPhone 15', 'SN-APL-IP15-003', 4, '2024-06-15', '2026-06-15', 'In Use'),
('MON-3001', 'Monitor', 'LG', 'UltraFine 27', 'SN-LG-UF27-004', 1, '2022-09-01', '2025-09-01', 'In Repair'),
('LAP-1003', 'Laptop', 'HP', 'EliteBook 840', 'SN-HP-840-005', NULL, '2025-01-08', '2028-01-08', 'In Stock');

INSERT INTO tickets (title, description, priority, status, category, opened_by_user_id, assigned_team, created_at, updated_at) VALUES
('Laptop will not connect to VPN', 'User reports repeated VPN failures on home broadband. Error appears after MFA approval.', 'High', 'Open', 'Network', 1, 'Service Desk', '2026-03-18 09:15:00', '2026-03-18 10:00:00'),
('Monitor flickering intermittently', 'External display flickers after waking from sleep. Suspected cable or dock issue.', 'Medium', 'In Progress', 'Hardware', 1, 'End User Computing', '2026-03-17 14:20:00', '2026-03-18 08:30:00'),
('Password reset not syncing to email', 'User changed AD password but mobile mail app still rejects credentials.', 'High', 'Resolved', 'Identity', 3, 'Identity Team', '2026-03-15 11:00:00', '2026-03-15 15:45:00'),
('New starter laptop request', 'Prepare and assign a standard laptop build for new joiner starting next Monday.', 'Low', 'Open', 'Provisioning', 5, 'Asset Team', '2026-03-19 13:10:00', '2026-03-19 13:10:00'),
('Slow performance on finance laptop', 'Laptop becomes slow when opening spreadsheets and Teams calls together.', 'Medium', 'Open', 'Performance', 1, 'End User Computing', '2026-03-20 10:25:00', '2026-03-20 10:25:00');

INSERT INTO knowledge_articles (title, category, body, author, created_at) VALUES
('How to troubleshoot VPN failures', 'Network',
'Check whether the user can reach the internet, confirm the VPN client version, verify MFA success, and review whether split tunnelling policies changed. If the issue started after a password change, test cached credentials and re-authentication.',
'Ben Morris', '2026-03-01 09:00:00'),

('Resolving monitor flicker on USB-C docks', 'Hardware',
'Monitor flicker is commonly caused by cable quality, dock firmware, refresh rate mismatch, or power-saving behaviour. Test with a direct cable, update dock firmware, and confirm display settings after wake from sleep.',
'Ben Morris', '2026-02-25 10:30:00'),

('Mobile mail still prompting after password reset', 'Identity',
'If a password has been reset, mobile mail clients may continue using cached credentials. Remove and re-add the account or update saved credentials in the mail application. In some cases conditional access delays can cause short-lived sign-in failures.',
'Chloe Singh', '2026-02-28 16:00:00'),

('Standard new starter laptop process', 'Provisioning',
'Assign an available device from stock, apply the standard image, confirm encryption, install endpoint protection, enrol into device management, and record the asset assignment against the user before handover.',
'Emma Hughes', '2026-03-05 08:45:00');
