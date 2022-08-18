CREATE TABLE `vsx` (
  `OID` varchar(50) NOT NULL,
  `n_OID` varchar(50) DEFAULT NULL,
  `Name` varchar(50) DEFAULT NULL,
  `V` varchar(50) DEFAULT NULL,
  `Type` varchar(50) DEFAULT NULL,
  `l_max` varchar(50) DEFAULT NULL,
  `max` varchar(50) DEFAULT NULL,
  `u_max` varchar(50) DEFAULT NULL,
  `n_max` varchar(50) DEFAULT NULL,
  `f_min` varchar(50) DEFAULT NULL,
  `l_min` varchar(50) DEFAULT NULL,
  `min` varchar(50) DEFAULT NULL,
  `u_min` varchar(50) DEFAULT NULL,
  `n_min` varchar(50) DEFAULT NULL,
  `l_Period` varchar(50) DEFAULT NULL,
  `Period` varchar(50) DEFAULT NULL,
  `u_Period` varchar(50) DEFAULT NULL,
  `RAJ2000` varchar(50) DEFAULT NULL,
  `DEJ2000` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`OID`)
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 PAGE_CHECKSUM=1 TRANSACTIONAL=0;

CREATE TABLE `curve` (
  `OID` varchar(50) NOT NULL,
  `SUB` varchar(50) NOT NULL,
  `author` varchar(50) DEFAULT NULL,
  `dec` varchar(50) DEFAULT NULL,
  `ra` varchar(50) DEFAULT NULL,
  `distance` varchar(50) DEFAULT NULL,
  `exptime` varchar(50) DEFAULT NULL,
  `mission` varchar(50) DEFAULT NULL,
  `zone` varchar(50) DEFAULT NULL,
  `target_name` varchar(50) DEFAULT NULL,
  `year` varchar(50) DEFAULT NULL,
  `filename` text DEFAULT NULL,
  PRIMARY KEY (`OID`, `SUB`)
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 PAGE_CHECKSUM=1 TRANSACTIONAL=0;

CREATE TABLE `meta` (
  `OID` varchar(50) NOT NULL,
  `SUB` varchar(50) NOT NULL,
  `data` json,
  PRIMARY KEY (`OID`, `SUB`)
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 PAGE_CHECKSUM=1 TRANSACTIONAL=0;
