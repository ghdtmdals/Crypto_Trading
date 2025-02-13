-- Sentiment 함수
-- 정의 불가 시 mysql root 계정 접근
-- SET GLOBAL log_bin_trust_function_creators = ON;
-- 완료 후
-- set global log_bin_trust_function_creators=off;
-- DELIMITER $$

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
END;

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
END;

CREATE FUNCTION IF NOT EXISTS SENTIMENT_RATIO(sentiment_days INT, alpha FLOAT(3, 2))
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

	SET sentiment_value = pos_neg_ratio * (1 - neutral_ratio * alpha);
	RETURN sentiment_value;
END;

-- DELIMITER ;
