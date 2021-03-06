CREATE TABLE `versions` (
	`id` INTEGER(11) NOT NULL AUTO_INCREMENT,
	`filename` VARCHAR(20),
	`version_date` DATE,
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


CREATE TABLE `location` (
  `id` INTEGER(11) NOT NUll AUTO_INCREMENT,
  `uic_code` VARCHAR(7),
  `end_date` DATE,
  `start_date` DATE,
  `quote_date` DATE,
  `admin_area_code` VARCHAR(3),
  `nlc` VARCHAR(4),
  `description` VARCHAR(16),
  `crs_code` VARCHAR(3),
  `resv_code` VARCHAR(5),
  `ers_country` VARCHAR(3),
  `ers_code` VARCHAR(3),
  `fare_group` VARCHAR(6),
  `county` VARCHAR(2),
  `pte_code` VARCHAR(2),
  `zone_no` VARCHAR(4),
  `zone_ind` VARCHAR(2),
  `region` VARCHAR(1),
  `hierarchy` VARCHAR(1),
  `cc_desc_out` VARCHAR(41),
  `cc_desc_rtn` VARCHAR(16),
  `atb_desc_out` VARCHAR(60),
  `atb_desc_rtn` VARCHAR(30),
  `special_facilities` VARCHAR(26),
  `lul_direction_ind` VARCHAR(1),
  `lul_uts_mode` VARCHAR(1),
  `lul_zone_1` VARCHAR(1),
  `lul_zone_2` VARCHAR(1),
  `lul_zone_3` VARCHAR(1),
  `lul_zone_4` VARCHAR(1),
  `lul_zone_5` VARCHAR(1),
  `lul_zone_6` VARCHAR(1),
  `lul_uts_london_stn` INT(1),
  `uts_code` VARCHAR(3),
  `uts_a_code` VARCHAR(3),
  `uts_ptr_bias` VARCHAR(3),
  `uts_offset` VARCHAR(1),
  `uts_north` VARCHAR(3),
  `uts_east` VARCHAR(3),
  `uts_south` VARCHAR(3),
  `uts_west` VARCHAR(3),
  `created_version` INTEGER(11),
  `deleted_version` INTEGER (11) NULL,
  PRIMARY KEY (`id`),
  INDEX idx_uic_code (`uic_code`),
  INDEX idx_uic_code_end_date (`uic_code`, `end_date`),
  INDEX idx_uic_code_created_version_deleted_version (`uic_code`,  `created_version`, `deleted_version`),
  INDEX idx_uic_code_end_date_created_version_deleted_version (`uic_code`, `end_date`, `created_version`, `deleted_version`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

CREATE TABLE `railcard_geography` (
  `id` INTEGER(11) NOT NUll AUTO_INCREMENT,
  `uic_code` VARCHAR(7),
  `railcard_code` VARCHAR(3),
  `end_date` DATE,
  `created_version` INTEGER(11),
  `deleted_version` INTEGER (11) NULL,
  PRIMARY KEY (`id`),
  INDEX idx_uic_code (`uic_code`),
  INDEX idx_uic_code_railcard_code (`uic_code`, `railcard_code`),
  INDEX idx_uic_code_railcard_code_created_version_deleted_version (`uic_code`, `railcard_code`, `created_version`, `deleted_version`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

CREATE TABLE `tt_group_location` (
  `id` INTEGER(11) NOT NUll AUTO_INCREMENT,
  `group_uic_code` VARCHAR(7),
  `end_date` DATE,
  `start_date` DATE,
  `quote_date` DATE,
  `descriptipn` VARCHAR(16),
  `ers_country` VARCHAR(3),
  `ers_code` VARCHAR(3),
  `created_version` INTEGER(11),
  `deleted_version` INTEGER (11) NULL,
  PRIMARY KEY (`id`),
  INDEX idx_group_uic_code (`group_uic_code`),
  INDEX idx_group_uic_code_end_date (`group_uic_code`, `end_date`),
  INDEX idx_group_uic_code_end_date_created_version_deleted_version (`group_uic_code`, `end_date`, `created_version`, `deleted_version`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

CREATE TABLE `group_member` (
  `id` INTEGER(11) NOT NUll AUTO_INCREMENT,
  `group_uic_code` VARCHAR(7),
  `end_date` DATE,
  `member_uic_code` VARCHAR(7),
  `member_crs_code` VARCHAR(3),
  `created_version` INTEGER(11),
  `deleted_version` INTEGER (11) NULL,
  PRIMARY KEY (`id`),
  INDEX idx_group_uic_code (`group_uic_code`),
  INDEX idx_member_uic_code (`member_uic_code`),
  INDEX idx_group_uic_code_end_date (`group_uic_code`, `end_date`),
  INDEX idx_group_uic_code_end_date_created_version_deleted_version (`group_uic_code`, `end_date`, `created_version`, `deleted_version`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

CREATE TABLE `synonym` (
  `id` INTEGER(11) NOT NUll AUTO_INCREMENT,
  `uic_code` VARCHAR(7),
  `end_date` DATE,
  `start_date` DATE,
  `descriptipn` VARCHAR(16),
  `created_version` INTEGER(11),
  `deleted_version` INTEGER (11) NULL,
  PRIMARY KEY (`id`),
  INDEX idx_group_uic_code (`group_uic_code`),
  INDEX idx_member_uic_code (`member_uic_code`),
  INDEX idx_group_uic_code_end_date (`group_uic_code`, `end_date`),
  INDEX idx_group_uic_code_end_date_created_version_deleted_version (`group_uic_code`, `end_date`, `created_version`, `deleted_version`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

