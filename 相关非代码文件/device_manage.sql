/*
 Navicat Premium Data Transfer

 Source Server         : MYSQL-8.0
 Source Server Type    : MySQL
 Source Server Version : 80034
 Source Host           : localhost:3306
 Source Schema         : device_manage

 Target Server Type    : MySQL
 Target Server Version : 80034
 File Encoding         : 65001

 Date: 20/11/2024 22:01:09
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for device
-- ----------------------------
DROP TABLE IF EXISTS `device`;
CREATE TABLE `device`  (
  `did` bigint NOT NULL COMMENT '主键，使用雪花算法生成',
  `dname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '设备名称',
  `d_created_time` timestamp NOT NULL COMMENT '设备创建时间（时间戳）',
  `d_last_update` timestamp NOT NULL COMMENT '设备上一次更新时间（时间戳）',
  `hardware_sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '硬件序列号SN',
  `hardware_model` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '硬件型号Model',
  `nic_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '网卡类型',
  `nic_ipv4` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '网卡IPv4',
  `nic_mac` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '网卡MAC地址',
  `wifi_mac` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'WIFI网卡MAC地址',
  `lte_imei` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'LTE IMEI编码，SIM 卡唯一标识',
  `salt` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '加密盐',
  `secret` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码+盐经过sha256哈希散列加密后的密钥',
  `software_version` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '驱动程序版本号',
  `software_last_update` datetime NOT NULL COMMENT '驱动程序最近更新时间',
  `status` int NOT NULL DEFAULT 0 COMMENT '设备状态0启用，1禁用，2删除',
  PRIMARY KEY (`did`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of device
-- ----------------------------

-- ----------------------------
-- Table structure for device_group
-- ----------------------------
DROP TABLE IF EXISTS `device_group`;
CREATE TABLE `device_group`  (
  `gid` bigint NOT NULL COMMENT '主键，使用雪花算法生成',
  `gname` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '分组名称',
  `g_created_time` timestamp NOT NULL COMMENT '分组创建时间',
  `g_last_update` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '分组更新时间',
  `g_status` int(10) UNSIGNED ZEROFILL NOT NULL COMMENT '状态：0存在，1删除',
  PRIMARY KEY (`gid`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of device_group
-- ----------------------------

-- ----------------------------
-- Table structure for relation
-- ----------------------------
DROP TABLE IF EXISTS `relation`;
CREATE TABLE `relation`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `did` bigint NULL DEFAULT NULL COMMENT '设备id',
  `gid` bigint NULL DEFAULT NULL COMMENT '分组id',
  `r_created_time` timestamp NOT NULL COMMENT '创建时间',
  `r_last_update` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `r_status` int(10) UNSIGNED ZEROFILL NOT NULL COMMENT '状态：0存在，1删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of relation
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
