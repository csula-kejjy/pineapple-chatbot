use chatbot_dev;
drop table crawler;
CREATE TABLE `chatbot_dev`.`crawler` ( 
	`idcrawler` INT NOT NULL AUTO_INCREMENT, 
	`url` LONGTEXT NULL DEFAULT NULL, 
	`keywords` LONGTEXT NULL DEFAULT NULL, 
	`category` TEXT NULL DEFAULT NULL, 
	`subcategory` TEXT NULL DEFAULT NULL,
PRIMARY KEY (`idcrawler`));