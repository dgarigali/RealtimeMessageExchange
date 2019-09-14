CREATE DATABASE `msg_exchange`;

DROP TABLE IF EXISTS `bot`;
DROP TABLE IF EXISTS `log`;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `building`;

# Create and insert data into building table

CREATE TABLE `building` (
  `id` varchar(50) NOT NULL,
  `name` varchar(100),
  `latitude` numeric(10,7),
  `longitude` numeric(10,7),
  `radious` float,
  PRIMARY KEY (`id`)
);

# Create and insert data into user table

CREATE TABLE `user` (
  `id` varchar(50) NOT NULL,
  `online` boolean,
  `latitude` numeric(10,7),
  `longitude` numeric(10,7),
  `b_id` varchar(50),
  `radious` float,
  `counter` int default 0,
  PRIMARY KEY (`id`),
  foreign key(b_id) references building(id)
);

# Create and insert data into bot table

CREATE TABLE `bot` (
  `id` varchar(50) NOT NULL,
  `b_id` varchar(50) NOT NULL,
  `online` boolean,
  `authorized` boolean NOT NULL,
  `pass` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  foreign key(b_id) references building(id)
);

# Create and insert data into log table

CREATE TABLE `log` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `message` varchar(250) NOT NULL,
  `u_id` varchar(50),
  `b_id` varchar(50),
  `bot_id` varchar(50),
  `timestamp` timestamp NOT NULL,
  PRIMARY KEY (`id`),
  foreign key(u_id) references user(id),
  foreign key(b_id) references building(id),
  foreign key(bot_id) references bot(id)
);