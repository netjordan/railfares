CREATE TABLE `versions` (
	`id` INTEGER(11) NOT NULL AUTO_INCREMENT,
	`filename` VARCHAR(20),
	`version_date` TIMESTAMP NULL,
	`loaded_date` TIMESTAMP NULL,
	`active_date` TIMESTAMP NULL,
	PRIMARY KEY(`id`),
	INDEX idx_filename (`filename`)
) charset=utf8;

CREATE TABLE `toc` (
  `id` INTEGER(11) NOT NUll AUTO_INCREMENT,
  `toc_id` VARCHAR(2),
  `toc_name` VARCHAR(30),
  `reservation_system` VARCHAR(8),
  `active` ENUM('yes','no'),
  `created_version` INTEGER(11),
  `deleted_version` INTEGER (11) NULL,
  PRIMARY KEY (`id`),
  INDEX idx_toc_id (`toc_id`),
  INDEX idx_toc_id_created_version_deleted_version (`toc_id`, `created_version`, `deleted_version`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

CREATE TABLE `fare_toc` (
  `id` INTEGER(11) NOT NUll AUTO_INCREMENT,
  `fare_toc_id` VARCHAR(3),
  `toc_id` VARCHAR(2),
  `fare_toc_name` VARCHAR(30),
  `created_version` INTEGER(11),
  `deleted_version` INTEGER (11) NULL,
  PRIMARY KEY (`id`),
  INDEX idx_fare_toc_id (`fare_toc_id`),
  INDEX idx_fare_toc_id_created_version_deleted_version (`fare_toc_id`, `created_version`, `deleted_version`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;