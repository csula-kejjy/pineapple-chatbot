ALTER TABLE `chatbot_dev`.`crawler` 
ADD COLUMN `category` TEXT NULL DEFAULT NULL AFTER `keywords`,
ADD COLUMN `subcategory` TEXT NULL DEFAULT NULL AFTER `category`;