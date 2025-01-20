CREATE TABLE IF NOT EXISTS Crypto_Info (
	`token` VARCHAR(11) NOT NULL,
	english_name VARCHAR(30) NOT NULL,
	korean_name VARCHAR(11)	NOT NULL,
    CONSTRAINT Crypto_Info_PK PRIMARY KEY(`token`)
);

CREATE TABLE IF NOT EXISTS News (
	`id` INT PRIMARY KEY AUTO_INCREMENT,
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
	`target` VARCHAR(4) NOT NULL,
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