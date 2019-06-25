SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE TABLE IF NOT EXISTS `chacha`.`person` (
    `person_id` INT(11) NULL DEFAULT NULL,
    `age_first_seen` INT(2) NULL DEFAULT NULL COMMENT 'null = unknown',
    `gender` INT(1) NULL DEFAULT NULL COMMENT 'null = unknown\n1 = female\n2 = male',
    `date_first_seen` DATETIME NULL DEFAULT NULL,
    `city` INT(4) NULL DEFAULT NULL,
    `state` INT(2) NULL DEFAULT NULL,
    `region` INT(2) NULL DEFAULT NULL,
    `area_code` INT(4) NULL DEFAULT NULL,
    `zip_code` INT(5) NULL DEFAULT NULL,
    `post_count` INT(11) NULL DEFAULT NULL)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `chacha`.`message` (
    `message_id` INT(11) NULL DEFAULT NULL,
    `person_id` INT(11) NULL DEFAULT NULL,
    `category_id` INT(2) NULL DEFAULT NULL,
    `subcategory_id` INT(2) NULL DEFAULT NULL,
    `role_id` INT(1) NULL DEFAULT NULL,
    `source_id` INT(2) NULL DEFAULT NULL,
    `message_text` VARCHAR(161) NULL DEFAULT NULL,
    `message_date` DATETIME NULL DEFAULT NULL,
    `message_length` INT(3) NULL DEFAULT NULL)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `chacha`.`category` (
    `category_id` INT(2) NOT NULL,
    `category_name` VARCHAR(22) NOT NULL,
    PRIMARY KEY (`category_id`),
    UNIQUE INDEX `category_id_UNIQUE` (`category_id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `chacha`.`subcategory` (
    `subcategory_id` INT(2) NOT NULL,
    `subcategory_name` VARCHAR(27) NOT NULL,
    PRIMARY KEY (`subcategory_id`),
    UNIQUE INDEX `sub_category_name_UNIQUE` (`subcategory_name` ASC),
    UNIQUE INDEX `sub_category_id(2)_UNIQUE` (`subcategory_id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `chacha`.`state` (
    `state_id` INT(2) NOT NULL,
    `state_name` VARCHAR(2) NOT NULL,
    PRIMARY KEY (`state_id`),
    UNIQUE INDEX `state_id_UNIQUE` (`state_id` ASC),
    UNIQUE INDEX `state_name_UNIQUE` (`state_name` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `chacha`.`source` (
    `source_id` INT(2) NOT NULL,
    `source_name` VARCHAR(19) NOT NULL,
    PRIMARY KEY (`source_id`),
    UNIQUE INDEX `source_id_UNIQUE` (`source_id` ASC),
    UNIQUE INDEX `source_name_UNIQUE` (`source_name` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `chacha`.`role` (
    `role_id` INT(1) NOT NULL,
    `role_name` VARCHAR(14) NOT NULL,
    PRIMARY KEY (`role_id`),
    UNIQUE INDEX `role_id(1)_UNIQUE` (`role_id` ASC),
    UNIQUE INDEX `role_name_UNIQUE` (`role_name` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `chacha`.`region` (
    `region_id` INT(2) NOT NULL,
    `region_name` VARCHAR(21) NOT NULL,
    PRIMARY KEY (`region_id`),
    UNIQUE INDEX `region_id_UNIQUE` (`region_id` ASC),
    UNIQUE INDEX `name_UNIQUE` (`region_name` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `chacha`.`city` (
    `city_id` INT(4) NOT NULL,
    `city_name` VARCHAR(27) NOT NULL,
    PRIMARY KEY (`city_id`),
    UNIQUE INDEX `city_id_UNIQUE` (`city_id` ASC),
    UNIQUE INDEX `name_UNIQUE` (`city_name` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;