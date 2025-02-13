-- SHOW VARIABLES LIKE 'event%'; -- event_scheduler: ON 확인

-- SELECT * FROM information_schema.EVENTS; -- event_scheduler 리스트 확인

-- 90일 지난 데이터는 자동 삭제되도록 설정
CREATE EVENT IF NOT EXISTS DEL_NEWS_OVER_90DAYS
ON SCHEDULE EVERY 1 DAY
COMMENT "Delete News Records Over 90 Days"
DO
DELETE FROM News WHERE news_date <= DATE_SUB(CURDATE(), INTERVAL 90 DAY);

CREATE EVENT IF NOT EXISTS DEL_LOGS_OVER_90DAYS
ON SCHEDULE EVERY 1 DAY
COMMENT "Delete Log Records Over 90 Days"
DO
DELETE FROM Trade_Log WHERE trade_date <= DATE_SUB(CURDATE(), INTERVAL 90 DAY);

CREATE EVENT IF NOT EXISTS DEL_UPBIT_PRICES_OVER_90DAYS
ON SCHEDULE EVERY 1 DAY
COMMENT "Delete Upbit Price Records Over 90 Days"
DO
DELETE FROM Upbit WHERE trade_date_kst <= DATE_SUB(CURDATE(), INTERVAL 90 DAY);

