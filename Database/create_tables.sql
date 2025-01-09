CREATE TABLE IF NOT EXISTS Crypto_Info (
	`token` VARCHAR(11) NOT NULL,
	english_name VARCHAR(30) NOT NULL,
	korean_name VARCHAR(11)	NOT NULL,
    CONSTRAINT Crypto_Info_PK PRIMARY KEY(`token`)
);

CREATE TABLE IF NOT EXISTS News (
	`token` VARCHAR(30) NOT NULL,
	news_date DATE NOT NULL,
	news_source VARCHAR(10) NOT NULL,
	title VARCHAR(150) NOT NULL,
	sentiment VARCHAR(8) NOT NULL,
	CONSTRAINT News_FK FOREIGN KEY(`token`) REFERENCES Crypto_Info(`token`)
);

CREATE TABLE IF NOT EXISTS Trade_Log (
	`token` VARCHAR(11) NOT NULL,
	trade_date DATE NOT NULL,
	trade_time TIME NOT NULL,
	krw_balance INT UNSIGNED NOT NULL,
	token_balance DECIMAL(10, 8) UNSIGNED NOT NULL,
	trade_call VARCHAR(4) NOT NULL,
	trade_result JSON NOT NULL,
	CONSTRAINT Trade_Log_FK FOREIGN KEY(`token`) REFERENCES Crypto_Info(`token`)
);

CREATE TABLE IF NOT EXISTS Upbit (
	`token` VARCHAR(11) NOT NULL,
	trade_date_kst DATE NOT NULL,
	trade_time_kst TIME NOT NULL,
	high_price DECIMAL(12, 3) UNSIGNED NOT NULL,
	low_price DECIMAL(12, 3) UNSIGNED NOT NULL,
	opening_price DECIMAL(12, 3) UNSIGNED NOT NULL,
	trade_price DECIMAL(12, 3) UNSIGNED NOT NULL,
	signed_change_rate FLOAT(8, 6) SIGNED NOT NULL,
	warning TINYINT(1) NOT NULL,
	deposit_amount_soaring TINYINT(1) NOT NULL,
	global_price_differences TINYINT(1) NOT NULL,
	price_fluctuations TINYINT(1) NOT NULL,
	trading_volume_soaring TINYINT(1) NOT NULL,
	concentration_of_small_accounts TINYINT(1) NOT NULL,
	CONSTRAINT Upbit_FK FOREIGN KEY(`token`) REFERENCES Crypto_Info(`token`)
);

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

-- Sentiment 함수
-- 정의 불가 시 mysql root 계정 접근 후
-- set global log_bin_trust_function_creators=on;
-- 완료 후
-- set global log_bin_trust_function_creators=off;
DELIMITER //

CREATE FUNCTION IF NOT EXISTS AVG_SENTIMENT(sentiment_days INT)
RETURNS DECIMAL(4, 3)
DETERMINISTIC
BEGIN
	DECLARE sentiment_value DECIMAL(4, 3);

	SELECT AVG(sent_val) INTO sentiment_value
	FROM
	(SELECT CASE
	WHEN sentiment = "Positive" THEN 1
	WHEN sentiment = "Neutral" THEN 0
	WHEN sentiment = "Negative" THEN -1
	END AS sent_val
	FROM News
	WHERE news_date >= DATE_SUB(CURDATE(), INTERVAL sentiment_days DAY)) N;

	RETURN sentiment_value;
END //

CREATE FUNCTION IF NOT EXISTS POS_NEG_RATIO(sentiment_days INT)
RETURNS DECIMAL(4, 3)
DETERMINISTIC
BEGIN
    DECLARE pos_count INT;
    DECLARE neg_count INT;
    DECLARE sentiment_value DECIMAL(4, 3);

	SELECT COUNT(sentiment) INTO pos_count FROM News WHERE sentiment = "Positive" AND news_date >= DATE_SUB(CURDATE(), INTERVAL sentiment_days DAY);
	SELECT COUNT(sentiment) INTO neg_count FROM News WHERE sentiment = "Negative" AND news_date >= DATE_SUB(CURDATE(), INTERVAL sentiment_days DAY);

    IF (pos_count + neg_count) = 0 THEN
        RETURN 0;
    END IF;

    SET sentiment_value = (pos_count - neg_count) / (pos_count + neg_count);
    RETURN sentiment_value;
END //

CREATE FUNCTION IF NOT EXISTS SENTIMENT_RATIO(sentiment_days INT)
RETURNS DECIMAL(4, 3)
DETERMINISTIC
BEGIN
	DECLARE neutral_count INT;
	DECLARE neutral_ratio DECIMAL(4, 3);
	DECLARE pos_neg_ratio DECIMAL(4, 3);
	DECLARE sentiment_value DECIMAL(4, 3);

	SELECT COUNT(sentiment) INTO neutral_count FROM News WHERE sentiment = "Neutral" AND news_date >= DATE_SUB(CURDATE(), INTERVAL sentiment_days DAY);

	IF neutral_count = 0 THEN 
		SET neutral_ratio = 0;
	ELSE
		SELECT neutral_count / COUNT(sentiment) INTO neutral_ratio FROM News WHERE news_date >= DATE_SUB(CURDATE(), INTERVAL sentiment_days DAY);
	END IF;

	SELECT POS_NEG_RATIO(sentiment_days) INTO pos_neg_ratio;

	SET sentiment_value = pos_neg_ratio * (1 - neutral_ratio);
	RETURN sentiment_value;
END //

DELIMITER ;

SELECT *
FROM `Crypto_Info`;