BEGIN TRANSACTION;
CREATE TABLE discipline_topics (
                    discipline_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    PRIMARY KEY (discipline_id, topic_id),
                    FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (topic_id) REFERENCES topics(id)
                        ON DELETE CASCADE
                );
INSERT INTO "discipline_topics" VALUES(24,61,1);
INSERT INTO "discipline_topics" VALUES(29,62,1);
INSERT INTO "discipline_topics" VALUES(29,63,2);
INSERT INTO "discipline_topics" VALUES(29,64,3);
INSERT INTO "discipline_topics" VALUES(29,65,4);
CREATE TABLE disciplines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    order_index INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
INSERT INTO "disciplines" VALUES(24,'Лідерство',NULL,1,'2026-01-29 11:32:44','2026-01-29 11:47:00');
INSERT INTO "disciplines" VALUES(29,'ДКЛ',NULL,0,'2026-02-05 06:12:19','2026-02-05 06:12:19');
CREATE VIRTUAL TABLE disciplines_fts USING fts5(
                    name, description,
                    content='disciplines', content_rowid='id'
                );
INSERT INTO "disciplines_fts" VALUES('Лідерство',NULL);
INSERT INTO "disciplines_fts" VALUES('ДКЛ',NULL);
CREATE TABLE educational_programs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    level TEXT,
                    duration_hours INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                , year INTEGER NOT NULL DEFAULT 0);
INSERT INTO "educational_programs" VALUES(22,'L1C ЗЕВТ МАГІСТРИ 2025',NULL,'L1C',66,'2026-01-29 11:32:44','2026-01-30 12:20:16',2025);
INSERT INTO "educational_programs" VALUES(24,'ДКЛ 2025','Додаткового курсу лідерства зі здобувачами освіти, щодо розвитку моральних, 
інтелектуальних та психологічних компетенцій майбутніх офіцерів.',NULL,20,'2026-02-05 06:09:25','2026-02-05 06:09:25',2025);
CREATE TABLE lesson_questions (
                    lesson_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    PRIMARY KEY (lesson_id, question_id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id) 
                        ON DELETE CASCADE,
                    FOREIGN KEY (question_id) REFERENCES questions(id) 
                        ON DELETE CASCADE
                );
INSERT INTO "lesson_questions" VALUES(589,1604,1);
INSERT INTO "lesson_questions" VALUES(589,1605,2);
INSERT INTO "lesson_questions" VALUES(591,1606,1);
INSERT INTO "lesson_questions" VALUES(591,1607,2);
INSERT INTO "lesson_questions" VALUES(593,1608,1);
INSERT INTO "lesson_questions" VALUES(593,1609,2);
INSERT INTO "lesson_questions" VALUES(594,1610,1);
INSERT INTO "lesson_questions" VALUES(594,1611,2);
INSERT INTO "lesson_questions" VALUES(595,1613,1);
INSERT INTO "lesson_questions" VALUES(595,1614,2);
INSERT INTO "lesson_questions" VALUES(595,1615,3);
INSERT INTO "lesson_questions" VALUES(596,1618,1);
INSERT INTO "lesson_questions" VALUES(596,1619,2);
INSERT INTO "lesson_questions" VALUES(596,1620,3);
INSERT INTO "lesson_questions" VALUES(596,1621,4);
INSERT INTO "lesson_questions" VALUES(598,1624,1);
INSERT INTO "lesson_questions" VALUES(598,1625,2);
INSERT INTO "lesson_questions" VALUES(598,1626,3);
INSERT INTO "lesson_questions" VALUES(599,1629,1);
INSERT INTO "lesson_questions" VALUES(599,1630,2);
INSERT INTO "lesson_questions" VALUES(600,1633,1);
INSERT INTO "lesson_questions" VALUES(600,1634,2);
INSERT INTO "lesson_questions" VALUES(601,1637,1);
INSERT INTO "lesson_questions" VALUES(601,1638,2);
INSERT INTO "lesson_questions" VALUES(601,1639,3);
INSERT INTO "lesson_questions" VALUES(602,1642,1);
INSERT INTO "lesson_questions" VALUES(602,1643,2);
INSERT INTO "lesson_questions" VALUES(603,1646,1);
INSERT INTO "lesson_questions" VALUES(603,1647,2);
INSERT INTO "lesson_questions" VALUES(604,1650,1);
INSERT INTO "lesson_questions" VALUES(604,1651,2);
INSERT INTO "lesson_questions" VALUES(604,1652,3);
INSERT INTO "lesson_questions" VALUES(605,1655,1);
INSERT INTO "lesson_questions" VALUES(591,1656,3);
INSERT INTO "lesson_questions" VALUES(594,1657,3);
INSERT INTO "lesson_questions" VALUES(606,1658,1);
INSERT INTO "lesson_questions" VALUES(606,1659,2);
INSERT INTO "lesson_questions" VALUES(606,1660,3);
INSERT INTO "lesson_questions" VALUES(608,1664,1);
INSERT INTO "lesson_questions" VALUES(609,1665,1);
INSERT INTO "lesson_questions" VALUES(609,1666,2);
INSERT INTO "lesson_questions" VALUES(609,1667,3);
INSERT INTO "lesson_questions" VALUES(609,1668,4);
INSERT INTO "lesson_questions" VALUES(611,1669,1);
INSERT INTO "lesson_questions" VALUES(615,1674,1);
INSERT INTO "lesson_questions" VALUES(615,1675,2);
INSERT INTO "lesson_questions" VALUES(615,1676,3);
INSERT INTO "lesson_questions" VALUES(615,1677,4);
INSERT INTO "lesson_questions" VALUES(616,1678,1);
INSERT INTO "lesson_questions" VALUES(616,1679,2);
INSERT INTO "lesson_questions" VALUES(618,1680,1);
INSERT INTO "lesson_questions" VALUES(618,1681,2);
INSERT INTO "lesson_questions" VALUES(618,1682,3);
INSERT INTO "lesson_questions" VALUES(620,1683,1);
INSERT INTO "lesson_questions" VALUES(620,1684,2);
CREATE TABLE lesson_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                , synonyms TEXT);
INSERT INTO "lesson_types" VALUES(1,'Самостійна робота','2026-01-27 14:22:36','2026-01-27 14:22:36',NULL);
INSERT INTO "lesson_types" VALUES(2,'Лекція','2026-01-27 14:22:36','2026-01-27 14:22:36',NULL);
INSERT INTO "lesson_types" VALUES(3,'Групове заняття','2026-01-27 14:22:36','2026-01-27 14:22:36',NULL);
INSERT INTO "lesson_types" VALUES(4,'Практичне заняття','2026-01-27 14:22:36','2026-01-27 14:22:36',NULL);
INSERT INTO "lesson_types" VALUES(5,'Семінар','2026-01-27 14:22:36','2026-01-27 14:22:36',NULL);
INSERT INTO "lesson_types" VALUES(6,'Контрольне заняття','2026-01-27 14:22:36','2026-01-27 14:22:36',NULL);
CREATE TABLE lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    duration_hours REAL DEFAULT 1.0,
                    order_index INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                , lesson_type_id INTEGER, classroom_hours REAL, self_study_hours REAL);
INSERT INTO "lessons" VALUES(589,'Заняття 1. Проблема лідерства в контексті ціннісно-етичної парадигми сучасності',NULL,5.0,1,'2026-01-29 11:32:44','2026-01-29 11:49:11',2,2.0,3.0);
INSERT INTO "lessons" VALUES(591,'Заняття 2. Гендерні аспекти професійної діяльності офіцера',NULL,8.0,2,'2026-01-29 11:32:44','2026-01-29 11:49:33',3,2.0,6.0);
INSERT INTO "lessons" VALUES(593,'Заняття 3. Професіоналізм і лідерство офіцерського складу',NULL,5.0,3,'2026-01-29 11:32:44','2026-01-29 11:52:13',3,2.0,3.0);
INSERT INTO "lessons" VALUES(594,'Заняття 4. Управління особовим складом',NULL,5.0,4,'2026-01-29 11:32:44','2026-01-29 11:53:15',3,2.0,3.0);
INSERT INTO "lessons" VALUES(595,'Заняття 5. Організаційна культура та етичні проблеми керівника',NULL,5.0,5,'2026-01-29 11:32:44','2026-01-29 11:56:30',3,2.0,3.0);
INSERT INTO "lessons" VALUES(596,'Заняття 6. Огляд теорії керівництва',NULL,5.0,6,'2026-01-29 11:32:44','2026-01-29 11:57:32',3,2.0,3.0);
INSERT INTO "lessons" VALUES(598,'Заняття 7. Керівник, як організатор і вихователь колективу',NULL,2.0,7,'2026-01-29 11:32:44','2026-01-29 11:58:15',3,2.0,0.0);
INSERT INTO "lessons" VALUES(599,'Заняття 8. Практичні механізми використання методики ситуаційного лідерства в діяльності командира підрозділу.',NULL,4.0,8,'2026-01-29 11:32:44','2026-01-29 11:59:19',5,4.0,0.0);
INSERT INTO "lessons" VALUES(600,'Заняття 9. Девіантна поведінка на війні',NULL,5.0,9,'2026-01-29 11:32:44','2026-01-29 12:02:56',3,2.0,3.0);
INSERT INTO "lessons" VALUES(601,'Заняття 10. Прояв лідерства командирів в бойовій обстановці',NULL,8.0,10,'2026-01-29 11:32:44','2026-01-29 12:03:20',5,2.0,6.0);
INSERT INTO "lessons" VALUES(602,'Заняття 11. Стратегічні комунікації в Збройних Силах України.',NULL,2.0,11,'2026-01-29 11:32:44','2026-01-29 12:03:56',3,2.0,0.0);
INSERT INTO "lessons" VALUES(603,'Заняття 12. Психологія здорового способу життя та профілактика суїцидів.',NULL,5.0,12,'2026-01-29 11:32:44','2026-01-29 12:04:28',5,2.0,3.0);
INSERT INTO "lessons" VALUES(604,'Заняття 13. Заборонені засоби та методи ведення війни',NULL,5.0,13,'2026-01-29 11:32:44','2026-01-29 12:05:34',3,2.0,3.0);
INSERT INTO "lessons" VALUES(605,'Заняття 14. Контрольна робота',NULL,2.0,14,'2026-01-29 11:32:44','2026-01-29 12:10:52',6,2.0,0.0);
INSERT INTO "lessons" VALUES(606,'Заняття 1. Цінності військового лідера.',NULL,2.0,1,'2026-02-05 06:46:52','2026-02-05 14:23:35',2,2.0,0.0);
INSERT INTO "lessons" VALUES(607,'Самостійна робота. Основи теорій мотивації. X-Y теорія. Піраміди потреб.',NULL,0.0,2,'2026-02-05 06:50:40','2026-02-05 14:23:38',1,0.0,1.0);
INSERT INTO "lessons" VALUES(608,'Заняття 2. Ораторське мистецтво в діяльності військового лідера.',NULL,2.0,3,'2026-02-05 06:51:46','2026-02-05 14:23:40',2,2.0,0.0);
INSERT INTO "lessons" VALUES(609,'Заняття 1. Морально-ціннісний підхід до ефективної команди: роль допоміжних інструментів у зміцненні бойового Духу та згуртованості підрозділу.',NULL,2.0,1,'2026-02-05 06:55:18','2026-02-05 14:24:06',2,2.0,0.0);
INSERT INTO "lessons" VALUES(610,'Самостійна робота. Використання релігійних структур в рф як механізм ціннісно-світоглядного протистояння та засіб агресивної пропаганди.',NULL,1.0,2,'2026-02-05 06:55:38','2026-02-05 14:24:09',1,0.0,1.0);
INSERT INTO "lessons" VALUES(611,'Заняття 2. Формування ціннісної системи військовослужбовця.',NULL,2.0,3,'2026-02-05 06:56:19','2026-02-05 14:24:12',2,2.0,0.0);
INSERT INTO "lessons" VALUES(615,'Заняття 1. Вплив військових традицій та ритуалів в Збройних Силах України на підвищення морально-психологічного стану особового складу.',NULL,2.0,1,'2026-02-05 13:48:31','2026-02-05 13:48:31',2,2.0,0.0);
INSERT INTO "lessons" VALUES(616,'Заняття 2. Історична роль українського війська у державотворенні',NULL,2.0,3,'2026-02-05 13:53:56','2026-02-05 13:53:56',2,2.0,0.0);
INSERT INTO "lessons" VALUES(617,'Самостійна робота. Герої України – приклад для наслідування.',NULL,0.0,2,'2026-02-05 13:55:26','2026-02-05 13:55:35',1,0.0,1.0);
INSERT INTO "lessons" VALUES(618,'Заняття 1. Особистісні якості сержантського та офіцерського складу  як суб’єкта морального і психологічного впливу на особовий склад.',NULL,2.0,1,'2026-02-05 14:00:49','2026-02-05 14:02:01',2,2.0,0.0);
INSERT INTO "lessons" VALUES(619,'Самостійна робота. Індивідуальна робота командира в підрозділі.',NULL,0.0,2,'2026-02-05 14:01:14','2026-02-05 14:02:07',1,0.0,1.0);
INSERT INTO "lessons" VALUES(620,'Заняття 2. Оцінювання інформаційного середовища щодо інформаційних загроз.',NULL,2.0,3,'2026-02-05 14:01:47','2026-02-05 14:02:04',2,2.0,0.0);
CREATE VIRTUAL TABLE lessons_fts USING fts5(
                    title, description,
                    content='lessons', content_rowid='id'
                );
INSERT INTO "lessons_fts" VALUES('Заняття 1. Проблема лідерства в контексті ціннісно-етичної парадигми сучасності',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 2. Гендерні аспекти професійної діяльності офіцера',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 3. Професіоналізм і лідерство офіцерського складу',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 4. Управління особовим складом',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 5. Організаційна культура та етичні проблеми керівника',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 6. Огляд теорії керівництва',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 7. Керівник, як організатор і вихователь колективу',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 8. Практичні механізми використання методики ситуаційного лідерства в діяльності командира підрозділу.',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 9. Девіантна поведінка на війні',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 10. Прояв лідерства командирів в бойовій обстановці',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 11. Стратегічні комунікації в Збройних Силах України.',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 12. Психологія здорового способу життя та профілактика суїцидів.',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 13. Заборонені засоби та методи ведення війни',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 14. Контрольна робота',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 1. Цінності військового лідера.',NULL);
INSERT INTO "lessons_fts" VALUES('Самостійна робота. Основи теорій мотивації. X-Y теорія. Піраміди потреб.',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 2. Ораторське мистецтво в діяльності військового лідера.',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 1. Морально-ціннісний підхід до ефективної команди: роль допоміжних інструментів у зміцненні бойового Духу та згуртованості підрозділу.',NULL);
INSERT INTO "lessons_fts" VALUES('Самостійна робота. Використання релігійних структур в рф як механізм ціннісно-світоглядного протистояння та засіб агресивної пропаганди.',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 2. Формування ціннісної системи військовослужбовця.',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 1. Вплив військових традицій та ритуалів в Збройних Силах України на підвищення морально-психологічного стану особового складу.',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 2. Історична роль українського війська у державотворенні',NULL);
INSERT INTO "lessons_fts" VALUES('Самостійна робота. Герої України – приклад для наслідування.',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 1. Особистісні якості сержантського та офіцерського складу  як суб’єкта морального і психологічного впливу на особовий склад.',NULL);
INSERT INTO "lessons_fts" VALUES('Самостійна робота. Індивідуальна робота командира в підрозділі.',NULL);
INSERT INTO "lessons_fts" VALUES('Заняття 2. Оцінювання інформаційного середовища щодо інформаційних загроз.',NULL);
CREATE TABLE "material_associations" (
                    material_id INTEGER NOT NULL,
                    entity_type TEXT NOT NULL CHECK(entity_type IN
                        ('program', 'discipline', 'topic', 'lesson')),
                    entity_id INTEGER NOT NULL,
                    PRIMARY KEY (material_id, entity_type, entity_id),
                    FOREIGN KEY (material_id) REFERENCES methodical_materials(id)
                        ON DELETE CASCADE
                );
INSERT INTO "material_associations" VALUES(5,'lesson',560);
INSERT INTO "material_associations" VALUES(6,'lesson',560);
INSERT INTO "material_associations" VALUES(7,'lesson',560);
INSERT INTO "material_associations" VALUES(8,'lesson',560);
INSERT INTO "material_associations" VALUES(9,'program',22);
INSERT INTO "material_associations" VALUES(10,'program',22);
INSERT INTO "material_associations" VALUES(11,'program',22);
INSERT INTO "material_associations" VALUES(12,'lesson',589);
INSERT INTO "material_associations" VALUES(13,'lesson',589);
INSERT INTO "material_associations" VALUES(14,'lesson',589);
INSERT INTO "material_associations" VALUES(15,'lesson',591);
INSERT INTO "material_associations" VALUES(16,'lesson',591);
INSERT INTO "material_associations" VALUES(17,'lesson',593);
INSERT INTO "material_associations" VALUES(18,'lesson',593);
INSERT INTO "material_associations" VALUES(19,'lesson',594);
INSERT INTO "material_associations" VALUES(21,'lesson',595);
INSERT INTO "material_associations" VALUES(22,'lesson',595);
INSERT INTO "material_associations" VALUES(23,'lesson',595);
INSERT INTO "material_associations" VALUES(24,'lesson',596);
INSERT INTO "material_associations" VALUES(25,'lesson',596);
INSERT INTO "material_associations" VALUES(26,'lesson',596);
INSERT INTO "material_associations" VALUES(27,'lesson',598);
INSERT INTO "material_associations" VALUES(28,'lesson',598);
INSERT INTO "material_associations" VALUES(29,'lesson',599);
INSERT INTO "material_associations" VALUES(30,'lesson',599);
INSERT INTO "material_associations" VALUES(31,'lesson',599);
INSERT INTO "material_associations" VALUES(32,'lesson',600);
INSERT INTO "material_associations" VALUES(33,'lesson',600);
INSERT INTO "material_associations" VALUES(34,'lesson',600);
INSERT INTO "material_associations" VALUES(35,'lesson',601);
INSERT INTO "material_associations" VALUES(36,'lesson',601);
INSERT INTO "material_associations" VALUES(37,'lesson',601);
INSERT INTO "material_associations" VALUES(38,'lesson',602);
INSERT INTO "material_associations" VALUES(39,'lesson',602);
INSERT INTO "material_associations" VALUES(40,'lesson',602);
INSERT INTO "material_associations" VALUES(41,'lesson',603);
INSERT INTO "material_associations" VALUES(42,'lesson',604);
INSERT INTO "material_associations" VALUES(43,'lesson',604);
INSERT INTO "material_associations" VALUES(46,'lesson',605);
INSERT INTO "material_associations" VALUES(47,'lesson',605);
INSERT INTO "material_associations" VALUES(48,'lesson',605);
INSERT INTO "material_associations" VALUES(49,'lesson',605);
INSERT INTO "material_associations" VALUES(10,'program',23);
INSERT INTO "material_associations" VALUES(11,'program',23);
INSERT INTO "material_associations" VALUES(9,'program',23);
INSERT INTO "material_associations" VALUES(50,'lesson',591);
INSERT INTO "material_associations" VALUES(51,'lesson',591);
INSERT INTO "material_associations" VALUES(52,'lesson',593);
INSERT INTO "material_associations" VALUES(53,'lesson',594);
INSERT INTO "material_associations" VALUES(54,'lesson',598);
INSERT INTO "material_associations" VALUES(55,'lesson',599);
INSERT INTO "material_associations" VALUES(56,'lesson',600);
INSERT INTO "material_associations" VALUES(57,'lesson',601);
INSERT INTO "material_associations" VALUES(58,'lesson',601);
INSERT INTO "material_associations" VALUES(59,'lesson',602);
INSERT INTO "material_associations" VALUES(60,'lesson',603);
INSERT INTO "material_associations" VALUES(61,'lesson',604);
INSERT INTO "material_associations" VALUES(62,'lesson',589);
INSERT INTO "material_associations" VALUES(63,'lesson',589);
INSERT INTO "material_associations" VALUES(64,'lesson',591);
INSERT INTO "material_associations" VALUES(65,'lesson',593);
INSERT INTO "material_associations" VALUES(66,'lesson',594);
INSERT INTO "material_associations" VALUES(67,'lesson',595);
INSERT INTO "material_associations" VALUES(68,'lesson',596);
INSERT INTO "material_associations" VALUES(69,'lesson',596);
INSERT INTO "material_associations" VALUES(70,'lesson',598);
INSERT INTO "material_associations" VALUES(71,'lesson',598);
INSERT INTO "material_associations" VALUES(72,'lesson',599);
INSERT INTO "material_associations" VALUES(73,'lesson',599);
INSERT INTO "material_associations" VALUES(74,'lesson',600);
INSERT INTO "material_associations" VALUES(75,'lesson',600);
INSERT INTO "material_associations" VALUES(76,'lesson',601);
INSERT INTO "material_associations" VALUES(77,'lesson',601);
INSERT INTO "material_associations" VALUES(78,'lesson',602);
INSERT INTO "material_associations" VALUES(79,'lesson',602);
INSERT INTO "material_associations" VALUES(80,'lesson',603);
INSERT INTO "material_associations" VALUES(81,'lesson',603);
INSERT INTO "material_associations" VALUES(82,'lesson',604);
INSERT INTO "material_associations" VALUES(83,'lesson',604);
INSERT INTO "material_associations" VALUES(84,'program',24);
INSERT INTO "material_associations" VALUES(85,'lesson',606);
INSERT INTO "material_associations" VALUES(86,'lesson',606);
INSERT INTO "material_associations" VALUES(87,'lesson',606);
INSERT INTO "material_associations" VALUES(88,'lesson',607);
INSERT INTO "material_associations" VALUES(89,'lesson',607);
INSERT INTO "material_associations" VALUES(90,'lesson',608);
INSERT INTO "material_associations" VALUES(91,'lesson',608);
INSERT INTO "material_associations" VALUES(92,'lesson',608);
INSERT INTO "material_associations" VALUES(93,'lesson',611);
INSERT INTO "material_associations" VALUES(94,'lesson',611);
INSERT INTO "material_associations" VALUES(95,'lesson',611);
INSERT INTO "material_associations" VALUES(96,'lesson',610);
INSERT INTO "material_associations" VALUES(97,'lesson',610);
INSERT INTO "material_associations" VALUES(98,'lesson',609);
INSERT INTO "material_associations" VALUES(99,'lesson',609);
INSERT INTO "material_associations" VALUES(100,'lesson',609);
INSERT INTO "material_associations" VALUES(101,'lesson',615);
INSERT INTO "material_associations" VALUES(102,'lesson',615);
INSERT INTO "material_associations" VALUES(103,'lesson',615);
INSERT INTO "material_associations" VALUES(104,'lesson',616);
INSERT INTO "material_associations" VALUES(105,'lesson',616);
INSERT INTO "material_associations" VALUES(106,'lesson',616);
INSERT INTO "material_associations" VALUES(107,'lesson',618);
INSERT INTO "material_associations" VALUES(108,'lesson',618);
INSERT INTO "material_associations" VALUES(109,'lesson',618);
INSERT INTO "material_associations" VALUES(110,'lesson',620);
INSERT INTO "material_associations" VALUES(111,'lesson',620);
INSERT INTO "material_associations" VALUES(112,'lesson',620);
INSERT INTO "material_associations" VALUES(113,'lesson',619);
CREATE TABLE material_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
INSERT INTO "material_types" VALUES(1,'plan','2026-01-29 10:04:56','2026-01-29 10:04:56');
INSERT INTO "material_types" VALUES(2,'metod','2026-01-29 10:04:56','2026-01-29 13:41:54');
INSERT INTO "material_types" VALUES(3,'presentation','2026-01-29 10:04:56','2026-01-29 10:04:56');
INSERT INTO "material_types" VALUES(4,'attachment','2026-01-29 10:04:56','2026-01-29 10:04:56');
CREATE VIRTUAL TABLE materials_fts USING fts5(
                    title, description, file_name,
                    content='methodical_materials', content_rowid='id'
                );
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т.4.1 .pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'План 4.1 ГЗ.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 4.1 ГЗ.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'requirements.txt');
INSERT INTO "materials_fts" VALUES('проходка',NULL,'Проходка_Лідерство_L-1C_филипович_ЗЕВТ.xlsx');
INSERT INTO "materials_fts" VALUES('Освітньо професійна програма',NULL,'ОПП ВА  магістр 255 набір 2024.docx');
INSERT INTO "materials_fts" VALUES('витяг із прогрмою',NULL,'L1С витяг ЗЕВТ магістри.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т 1.1 Ціннісна парадигма.pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.1.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'+Т 1.1 - Проблема лідерства.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т 1.3 Презентація Гендерні аспекти проф діяльності.pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.3.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т 1.3 професіоналізм.pptx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'ПЗ Т 1.3 професіоналізм лідерство.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т 1.4 Управління.pptx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'1.5..pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.5.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.5 гз.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.12 гз.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.12.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т 1.12 Стилі керівництва та лідерства.pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.7.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.7 гз.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т 1.8 КС Практичні механізми Сит Лідерства.pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.8 КС.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.8 кс.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.9.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.9.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т 1.9 девіантна  поведінка.pptx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т 1.10 КС Прояв лідерства командирів в бойовій обстановці.pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'1.10 ПРОЯВ.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.10-(КС).docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'ПЗ Т 1.11 стратегічні комунікації.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.11 - (ГЗ-3).docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т 1.11 Стратегічні комунікації.pptx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.22 Круглий стол L.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'План 1.14 ГЗ.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.14 ГЗ.docx');
INSERT INTO "materials_fts" VALUES('білети',NULL,'білети.docx');
INSERT INTO "materials_fts" VALUES('кейси завдання',NULL,'ВЛ (кейси) завдання+.docx');
INSERT INTO "materials_fts" VALUES('методичка до заліку',NULL,'Методичка диф заліку+.docx');
INSERT INTO "materials_fts" VALUES('питання на залік',NULL,'питання на залік.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'+Т 1.2 - гендер.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'1.2. гендерні аспекти .pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'ПланЗ Т 1.3 професіоналізм лідерство.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план управління особовим складом.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'1.7.pptx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т.1.8.NEW.2025_EN.pptx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т.1.9.NEW.2025_EN.pptx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т.1.10_2025 .pptx');
INSERT INTO "materials_fts" VALUES('відеофільм',NULL,'307.mp4');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'2Т 1.11 Стратегічні комунікації.pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.12.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т.1.13 .pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.1.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'+Т 1.1 - Проблема лідерства.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.2.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.3 - (ГЗ-2).docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Теорія 1.4 управління.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.5 гз.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'1.6 теорія.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.6.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.7.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.7 гз.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.8 кс.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.8 КС.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.9.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.9.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.10 ПРОЯВ.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.10-(КС).docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'ПЗ Т 1.11 стратегічні комунікації.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.11 - (ГЗ-3).docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'план 1.12.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.12 Круглий стол L.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'План 1.13 ГЗ.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Т 1.13 ГЗ.docx');
INSERT INTO "materials_fts" VALUES('Навчальний план-програма',NULL,'Шкло+духовність ПРАВКА.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'метод 1.1. .docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'План_Т_1.1.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'Т.1.1.pptx');
INSERT INTO "materials_fts" VALUES('Завдання для викладача',NULL,'Завдання для викладача на СР до Т 1.1 л.doc');
INSERT INTO "materials_fts" VALUES('Завдання для курсантів',NULL,'Завдання для курсантів на СР до Т 1.1 л.doc');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'1.2..pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'_План_Т_1.2.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'метод 1.2. .docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'_План_Т_4.2 – копія.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'_метод 4.2.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'4.2.pptx');
INSERT INTO "materials_fts" VALUES('Завдання для викладача',NULL,'Завдання для викладача на СР до Т 4.1 л.doc');
INSERT INTO "materials_fts" VALUES('Завдання для курсантів на',NULL,'Завдання для курсантів на СР до Т 4.1 л.doc');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'4.1..pptx');
INSERT INTO "materials_fts" VALUES('план',NULL,'План_Т_4.1_гз.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'4.1..pptx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Історія 1 лекція Методичка.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'Пл_Пр_Л_Т 2_1.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'преза шкло 1.pptm');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'преза шкло 2.pptm');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'Історія 2 лекція меточка.docx');
INSERT INTO "materials_fts" VALUES('план',NULL,'Пл_Пр_Л_Т 2_2.docx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'МПЗ  Т 3_1_ ГЗ.doc');
INSERT INTO "materials_fts" VALUES('план',NULL,'План_Т_3.1_іл_Шкло.docx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'ВК та ППП_Т 3.1 Шкло.pptx');
INSERT INTO "materials_fts" VALUES('презентація',NULL,'ВК та_ППП_ Т 3.2 інформаційні навички додатково.pptx');
INSERT INTO "materials_fts" VALUES('методичка',NULL,'МПЗ  Т 3.2 Л_інформаційна гігієна.doc');
INSERT INTO "materials_fts" VALUES('план',NULL,'План_Т_3.2_іл_Шкло.docx');
INSERT INTO "materials_fts" VALUES('самостійна робота',NULL,'ВКта ППП  3 самостійна робота.docx');
CREATE TABLE "methodical_materials" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                material_type TEXT NOT NULL,
                description TEXT,
                original_filename TEXT,
                stored_filename TEXT,
                relative_path TEXT,
                file_type TEXT,
                file_path TEXT,
                file_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
INSERT INTO "methodical_materials" VALUES(5,'презентація','presentation',NULL,'Т.4.1 .pptx','m_000005.pptx','p21/d23/m_000005.pptx','pptx','p21/d23/m_000005.pptx','Т.4.1 .pptx','2026-01-29 10:05:41','2026-01-29 10:25:22');
INSERT INTO "methodical_materials" VALUES(6,'план','plan',NULL,'План 4.1 ГЗ.docx','m_000006.docx','p21/d23/m_000006.docx','docx','p21/d23/m_000006.docx','План 4.1 ГЗ.docx','2026-01-29 10:06:18','2026-01-29 10:25:02');
INSERT INTO "methodical_materials" VALUES(7,'методичка','guide',NULL,'Т 4.1 ГЗ.docx','m_000007.docx','p21/d23/m_000007.docx','docx','p21/d23/m_000007.docx','Т 4.1 ГЗ.docx','2026-01-29 10:07:33','2026-01-29 10:24:53');
INSERT INTO "methodical_materials" VALUES(8,'план','attachment',NULL,'requirements.txt','m_000008.txt','p21/d23/m_000008.txt','txt','p21/d23/m_000008.txt','requirements.txt','2026-01-29 10:29:52','2026-01-29 10:29:52');
INSERT INTO "methodical_materials" VALUES(9,'проходка','attachment',NULL,'Проходка_Лідерство_L-1C_филипович_ЗЕВТ.xlsx','m_000009.xlsx','p22/d24/m_000009.xlsx','xlsx','p22/d24/m_000009.xlsx','Проходка_Лідерство_L-1C_филипович_ЗЕВТ.xlsx','2026-01-29 11:40:46','2026-01-29 11:40:46');
INSERT INTO "methodical_materials" VALUES(10,'Освітньо професійна програма','attachment',NULL,'ОПП ВА  магістр 255 набір 2024.docx','m_000010.docx','p22/d24/m_000010.docx','docx','p22/d24/m_000010.docx','ОПП ВА  магістр 255 набір 2024.docx','2026-01-29 11:44:02','2026-01-29 11:44:02');
INSERT INTO "methodical_materials" VALUES(11,'витяг із прогрмою','attachment',NULL,'L1С витяг ЗЕВТ магістри.docx','m_000011.docx','p22/d24/m_000011.docx','docx','p22/d24/m_000011.docx','L1С витяг ЗЕВТ магістри.docx','2026-01-29 11:44:23','2026-01-29 11:44:24');
INSERT INTO "methodical_materials" VALUES(12,'презентація','presentation',NULL,'Т 1.1 Ціннісна парадигма.pptx','m_000012.pptx','p22/d24/m_000012.pptx','pptx','p22/d24/m_000012.pptx','Т 1.1 Ціннісна парадигма.pptx','2026-01-29 12:06:41','2026-01-29 12:06:41');
INSERT INTO "methodical_materials" VALUES(13,'план','plan',NULL,'план 1.1.docx','m_000013.docx','p22/d24/m_000013.docx','docx','p22/d24/m_000013.docx','план 1.1.docx','2026-01-29 12:07:00','2026-01-29 12:07:00');
INSERT INTO "methodical_materials" VALUES(14,'методичка','metod',NULL,'+Т 1.1 - Проблема лідерства.docx','m_000014.docx','p22/d24/m_000014.docx','docx','p22/d24/m_000014.docx','+Т 1.1 - Проблема лідерства.docx','2026-01-29 12:07:17','2026-01-30 06:50:38');
INSERT INTO "methodical_materials" VALUES(15,'презентація','presentation',NULL,'Т 1.3 Презентація Гендерні аспекти проф діяльності.pptx','m_000015.pptx','p22/d24/m_000015.pptx','pptx','p22/d24/m_000015.pptx','Т 1.3 Презентація Гендерні аспекти проф діяльності.pptx','2026-01-29 13:39:04','2026-01-29 13:39:04');
INSERT INTO "methodical_materials" VALUES(16,'план','plan',NULL,'план 1.3.docx','m_000016.docx','p22/d24/m_000016.docx','docx','p22/d24/m_000016.docx','план 1.3.docx','2026-01-29 13:39:18','2026-01-29 13:39:18');
INSERT INTO "methodical_materials" VALUES(17,'презентація','presentation',NULL,'Т 1.3 професіоналізм.pptx','m_000017.pptx','p22/d24/m_000017.pptx','pptx','p22/d24/m_000017.pptx','Т 1.3 професіоналізм.pptx','2026-01-29 13:39:38','2026-01-29 13:39:38');
INSERT INTO "methodical_materials" VALUES(18,'методичка','metod',NULL,'ПЗ Т 1.3 професіоналізм лідерство.docx','m_000018.docx','p22/d24/m_000018.docx','docx','p22/d24/m_000018.docx','ПЗ Т 1.3 професіоналізм лідерство.docx','2026-01-29 13:40:11','2026-01-30 06:51:26');
INSERT INTO "methodical_materials" VALUES(19,'презентація','presentation',NULL,'Т 1.4 Управління.pptx','m_000019.pptx','p22/d24/m_000019.pptx','pptx','p22/d24/m_000019.pptx','Т 1.4 Управління.pptx','2026-01-29 13:40:45','2026-01-29 13:40:45');
INSERT INTO "methodical_materials" VALUES(21,'презентація','presentation',NULL,'1.5..pptx','m_000021.pptx','p22/d24/m_000021.pptx','pptx','p22/d24/m_000021.pptx','1.5..pptx','2026-01-29 13:41:09','2026-01-30 06:52:40');
INSERT INTO "methodical_materials" VALUES(22,'план','plan',NULL,'план 1.5.docx','m_000022.docx','p22/d24/m_000022.docx','docx','p22/d24/m_000022.docx','план 1.5.docx','2026-01-29 13:41:19','2026-01-30 06:52:36');
INSERT INTO "methodical_materials" VALUES(23,'методичка','metod',NULL,'Т 1.5 гз.docx','m_000023.docx','p22/d24/m_000023.docx','docx','p22/d24/m_000023.docx','Т 1.5 гз.docx','2026-01-29 13:41:32','2026-01-30 06:53:35');
INSERT INTO "methodical_materials" VALUES(24,'методичка','metod',NULL,'Т 1.12 гз.docx','m_000024.docx','p22/d24/m_000024.docx','docx','p22/d24/m_000024.docx','Т 1.12 гз.docx','2026-01-29 13:43:04','2026-01-29 13:43:04');
INSERT INTO "methodical_materials" VALUES(25,'план','plan',NULL,'план 1.12.docx','m_000025.docx','p22/d24/m_000025.docx','docx','p22/d24/m_000025.docx','план 1.12.docx','2026-01-29 13:43:15','2026-01-29 13:43:15');
INSERT INTO "methodical_materials" VALUES(26,'презентація','presentation',NULL,'Т 1.12 Стилі керівництва та лідерства.pptx','m_000026.pptx','p22/d24/m_000026.pptx','pptx','p22/d24/m_000026.pptx','Т 1.12 Стилі керівництва та лідерства.pptx','2026-01-29 13:43:24','2026-01-29 13:43:24');
INSERT INTO "methodical_materials" VALUES(27,'план','plan',NULL,'план 1.7.docx','m_000027.docx','p22/d24/m_000027.docx','docx','p22/d24/m_000027.docx','план 1.7.docx','2026-01-29 13:43:41','2026-01-29 13:43:41');
INSERT INTO "methodical_materials" VALUES(28,'методичка','metod',NULL,'Т 1.7 гз.docx','m_000028.docx','p22/d24/m_000028.docx','docx','p22/d24/m_000028.docx','Т 1.7 гз.docx','2026-01-29 13:43:52','2026-01-29 13:43:52');
INSERT INTO "methodical_materials" VALUES(29,'презентація','presentation',NULL,'Т 1.8 КС Практичні механізми Сит Лідерства.pptx','m_000029.pptx','p22/d24/m_000029.pptx','pptx','p22/d24/m_000029.pptx','Т 1.8 КС Практичні механізми Сит Лідерства.pptx','2026-01-29 13:44:11','2026-01-29 13:44:11');
INSERT INTO "methodical_materials" VALUES(30,'план','plan',NULL,'план 1.8 КС.docx','m_000030.docx','p22/d24/m_000030.docx','docx','p22/d24/m_000030.docx','план 1.8 КС.docx','2026-01-29 13:44:21','2026-01-29 13:44:21');
INSERT INTO "methodical_materials" VALUES(31,'методичка','metod',NULL,'Т 1.8 кс.docx','m_000031.docx','p22/d24/m_000031.docx','docx','p22/d24/m_000031.docx','Т 1.8 кс.docx','2026-01-29 13:44:32','2026-01-29 13:44:32');
INSERT INTO "methodical_materials" VALUES(32,'план','plan',NULL,'план 1.9.docx','m_000032.docx','p22/d24/m_000032.docx','docx','p22/d24/m_000032.docx','план 1.9.docx','2026-01-29 13:44:49','2026-01-29 13:44:49');
INSERT INTO "methodical_materials" VALUES(33,'методичка','metod',NULL,'Т 1.9.docx','m_000033.docx','p22/d24/m_000033.docx','docx','p22/d24/m_000033.docx','Т 1.9.docx','2026-01-29 13:45:01','2026-01-29 13:45:01');
INSERT INTO "methodical_materials" VALUES(34,'презентація','presentation',NULL,'Т 1.9 девіантна  поведінка.pptx','m_000034.pptx','p22/d24/m_000034.pptx','pptx','p22/d24/m_000034.pptx','Т 1.9 девіантна  поведінка.pptx','2026-01-29 13:45:15','2026-01-30 06:56:27');
INSERT INTO "methodical_materials" VALUES(35,'презентація','presentation',NULL,'Т 1.10 КС Прояв лідерства командирів в бойовій обстановці.pptx','m_000035.pptx','p22/d24/m_000035.pptx','pptx','p22/d24/m_000035.pptx','Т 1.10 КС Прояв лідерства командирів в бойовій обстановці.pptx','2026-01-29 13:45:32','2026-01-29 13:45:32');
INSERT INTO "methodical_materials" VALUES(36,'план','plan',NULL,'1.10 ПРОЯВ.docx','m_000036.docx','p22/d24/m_000036.docx','docx','p22/d24/m_000036.docx','1.10 ПРОЯВ.docx','2026-01-29 13:46:01','2026-01-29 13:46:01');
INSERT INTO "methodical_materials" VALUES(37,'методичка','metod',NULL,'Т 1.10-(КС).docx','m_000037.docx','p22/d24/m_000037.docx','docx','p22/d24/m_000037.docx','Т 1.10-(КС).docx','2026-01-29 13:46:10','2026-01-29 13:46:10');
INSERT INTO "methodical_materials" VALUES(38,'план','plan',NULL,'ПЗ Т 1.11 стратегічні комунікації.docx','m_000038.docx','p22/d24/m_000038.docx','docx','p22/d24/m_000038.docx','ПЗ Т 1.11 стратегічні комунікації.docx','2026-01-29 13:46:31','2026-01-29 13:46:31');
INSERT INTO "methodical_materials" VALUES(39,'методичка','metod',NULL,'Т 1.11 - (ГЗ-3).docx','m_000039.docx','p22/d24/m_000039.docx','docx','p22/d24/m_000039.docx','Т 1.11 - (ГЗ-3).docx','2026-01-29 13:46:44','2026-01-29 13:46:44');
INSERT INTO "methodical_materials" VALUES(40,'презентація','attachment',NULL,'Т 1.11 Стратегічні комунікації.pptx','m_000040.pptx','p22/d24/m_000040.pptx','pptx','p22/d24/m_000040.pptx','Т 1.11 Стратегічні комунікації.pptx','2026-01-29 13:46:52','2026-01-29 13:46:52');
INSERT INTO "methodical_materials" VALUES(41,'методичка','metod',NULL,'Т 1.22 Круглий стол L.docx','m_000041.docx','p22/d24/m_000041.docx','docx','p22/d24/m_000041.docx','Т 1.22 Круглий стол L.docx','2026-01-29 13:47:20','2026-01-29 13:47:20');
INSERT INTO "methodical_materials" VALUES(42,'план','plan',NULL,'План 1.14 ГЗ.docx','m_000042.docx','p22/d24/m_000042.docx','docx','p22/d24/m_000042.docx','План 1.14 ГЗ.docx','2026-01-29 13:47:46','2026-01-29 13:47:47');
INSERT INTO "methodical_materials" VALUES(43,'методичка','metod',NULL,'Т 1.14 ГЗ.docx','m_000043.docx','p22/d24/m_000043.docx','docx','p22/d24/m_000043.docx','Т 1.14 ГЗ.docx','2026-01-29 13:47:58','2026-01-29 13:47:58');
INSERT INTO "methodical_materials" VALUES(46,'білети','attachment',NULL,'білети.docx','m_000046.docx','p22/d24/m_000046.docx','docx','p22/d24/m_000046.docx','білети.docx','2026-01-29 13:48:48','2026-01-29 13:48:48');
INSERT INTO "methodical_materials" VALUES(47,'кейси завдання','attachment',NULL,'ВЛ (кейси) завдання+.docx','m_000047.docx','p22/d24/m_000047.docx','docx','p22/d24/m_000047.docx','ВЛ (кейси) завдання+.docx','2026-01-29 13:48:58','2026-01-29 13:48:58');
INSERT INTO "methodical_materials" VALUES(48,'методичка до заліку','attachment',NULL,'Методичка диф заліку+.docx','m_000048.docx','p22/d24/m_000048.docx','docx','p22/d24/m_000048.docx','Методичка диф заліку+.docx','2026-01-29 13:49:09','2026-01-29 13:49:09');
INSERT INTO "methodical_materials" VALUES(49,'питання на залік','attachment',NULL,'питання на залік.docx','m_000049.docx','p22/d24/m_000049.docx','docx','p22/d24/m_000049.docx','питання на залік.docx','2026-01-29 13:49:19','2026-01-29 13:49:19');
INSERT INTO "methodical_materials" VALUES(50,'методичка','metod',NULL,'+Т 1.2 - гендер.docx','m_000050.docx','p22/d24/m_000050.docx','docx','p22/d24/m_000050.docx','+Т 1.2 - гендер.docx','2026-01-30 06:33:01','2026-01-30 06:33:01');
INSERT INTO "methodical_materials" VALUES(51,'презентація','presentation',NULL,'1.2. гендерні аспекти .pptx','m_000051.pptx','p22/d24/m_000051.pptx','pptx','p22/d24/m_000051.pptx','1.2. гендерні аспекти .pptx','2026-01-30 06:33:13','2026-01-30 06:33:13');
INSERT INTO "methodical_materials" VALUES(52,'план','plan',NULL,'ПланЗ Т 1.3 професіоналізм лідерство.docx','m_000052.docx','p22/d24/m_000052.docx','docx','p22/d24/m_000052.docx','ПланЗ Т 1.3 професіоналізм лідерство.docx','2026-01-30 06:33:47','2026-01-30 06:33:48');
INSERT INTO "methodical_materials" VALUES(53,'план','plan',NULL,'план управління особовим складом.docx','m_000053.docx','p22/d24/m_000053.docx','docx','p22/d24/m_000053.docx','план управління особовим складом.docx','2026-01-30 06:34:30','2026-01-30 06:34:30');
INSERT INTO "methodical_materials" VALUES(54,'презентація','presentation',NULL,'1.7.pptx','m_000054.pptx','p22/d24/m_000054.pptx','pptx','p22/d24/m_000054.pptx','1.7.pptx','2026-01-30 06:35:23','2026-01-30 06:35:23');
INSERT INTO "methodical_materials" VALUES(55,'презентація','presentation',NULL,'Т.1.8.NEW.2025_EN.pptx','m_000055.pptx','p22/d24/m_000055.pptx','pptx','p22/d24/m_000055.pptx','Т.1.8.NEW.2025_EN.pptx','2026-01-30 06:35:53','2026-01-30 06:35:53');
INSERT INTO "methodical_materials" VALUES(56,'презентація','presentation',NULL,'Т.1.9.NEW.2025_EN.pptx','m_000056.pptx','p22/d24/m_000056.pptx','pptx','p22/d24/m_000056.pptx','Т.1.9.NEW.2025_EN.pptx','2026-01-30 06:36:33','2026-01-30 06:36:33');
INSERT INTO "methodical_materials" VALUES(57,'презентація','presentation',NULL,'Т.1.10_2025 .pptx','m_000057.pptx','p22/d24/m_000057.pptx','pptx','p22/d24/m_000057.pptx','Т.1.10_2025 .pptx','2026-01-30 06:37:18','2026-01-30 06:37:19');
INSERT INTO "methodical_materials" VALUES(58,'відеофільм','attachment',NULL,'307.mp4','m_000058.mp4','p22/d24/m_000058.mp4','mp4','p22/d24/m_000058.mp4','307.mp4','2026-01-30 06:37:34','2026-01-30 06:37:34');
INSERT INTO "methodical_materials" VALUES(59,'презентація','presentation',NULL,'2Т 1.11 Стратегічні комунікації.pptx','m_000059.pptx','p22/d24/m_000059.pptx','pptx','p22/d24/m_000059.pptx','2Т 1.11 Стратегічні комунікації.pptx','2026-01-30 06:38:07','2026-01-30 06:38:07');
INSERT INTO "methodical_materials" VALUES(60,'план','attachment',NULL,'план 1.12.docx','m_000060.docx','p22/d24/m_000060.docx','docx','p22/d24/m_000060.docx','план 1.12.docx','2026-01-30 06:38:41','2026-01-30 06:38:41');
INSERT INTO "methodical_materials" VALUES(61,'презентація','presentation',NULL,'Т.1.13 .pptx','m_000061.pptx','p22/d24/m_000061.pptx','pptx','p22/d24/m_000061.pptx','Т.1.13 .pptx','2026-01-30 06:39:16','2026-01-30 06:39:16');
INSERT INTO "methodical_materials" VALUES(62,'план','plan',NULL,'план 1.1.docx','m_000062.docx','p22/d24/m_000062.docx','docx','p22/d24/m_000062.docx','план 1.1.docx','2026-01-30 06:40:02','2026-01-30 06:40:02');
INSERT INTO "methodical_materials" VALUES(63,'методичка','metod',NULL,'+Т 1.1 - Проблема лідерства.docx','m_000063.docx','p22/d24/m_000063.docx','docx','p22/d24/m_000063.docx','+Т 1.1 - Проблема лідерства.docx','2026-01-30 06:40:19','2026-01-30 06:40:19');
INSERT INTO "methodical_materials" VALUES(64,'план','plan',NULL,'план 1.2.docx','m_000064.docx','p22/d24/m_000064.docx','docx','p22/d24/m_000064.docx','план 1.2.docx','2026-01-30 06:42:28','2026-01-30 06:42:28');
INSERT INTO "methodical_materials" VALUES(65,'методичка','metod',NULL,'Т 1.3 - (ГЗ-2).docx','m_000065.docx','p22/d24/m_000065.docx','docx','p22/d24/m_000065.docx','Т 1.3 - (ГЗ-2).docx','2026-01-30 06:43:15','2026-01-30 06:43:15');
INSERT INTO "methodical_materials" VALUES(66,'методичка','metod',NULL,'Теорія 1.4 управління.docx','m_000066.docx','p22/d24/m_000066.docx','docx','p22/d24/m_000066.docx','Теорія 1.4 управління.docx','2026-01-30 06:44:35','2026-01-30 06:44:35');
INSERT INTO "methodical_materials" VALUES(67,'методичка','attachment',NULL,'Т 1.5 гз.docx','m_000067.docx','p22/d24/m_000067.docx','docx','p22/d24/m_000067.docx','Т 1.5 гз.docx','2026-01-30 06:53:27','2026-01-30 06:53:27');
INSERT INTO "methodical_materials" VALUES(68,'методичка','metod',NULL,'1.6 теорія.docx','m_000068.docx','p22/d24/m_000068.docx','docx','p22/d24/m_000068.docx','1.6 теорія.docx','2026-01-30 06:53:59','2026-01-30 06:54:00');
INSERT INTO "methodical_materials" VALUES(69,'план','plan',NULL,'план 1.6.docx','m_000069.docx','p22/d24/m_000069.docx','docx','p22/d24/m_000069.docx','план 1.6.docx','2026-01-30 06:54:10','2026-01-30 06:54:10');
INSERT INTO "methodical_materials" VALUES(70,'план','plan',NULL,'план 1.7.docx','m_000070.docx','p22/d24/m_000070.docx','docx','p22/d24/m_000070.docx','план 1.7.docx','2026-01-30 06:54:38','2026-01-30 06:54:38');
INSERT INTO "methodical_materials" VALUES(71,'методичка','metod',NULL,'Т 1.7 гз.docx','m_000071.docx','p22/d24/m_000071.docx','docx','p22/d24/m_000071.docx','Т 1.7 гз.docx','2026-01-30 06:54:49','2026-01-30 06:54:49');
INSERT INTO "methodical_materials" VALUES(72,'методичка','metod',NULL,'Т 1.8 кс.docx','m_000072.docx','p22/d24/m_000072.docx','docx','p22/d24/m_000072.docx','Т 1.8 кс.docx','2026-01-30 06:55:05','2026-01-30 06:55:05');
INSERT INTO "methodical_materials" VALUES(73,'план','plan',NULL,'план 1.8 КС.docx','m_000073.docx','p22/d24/m_000073.docx','docx','p22/d24/m_000073.docx','план 1.8 КС.docx','2026-01-30 06:55:55','2026-01-30 06:55:55');
INSERT INTO "methodical_materials" VALUES(74,'методичка','metod',NULL,'Т 1.9.docx','m_000074.docx','p22/d24/m_000074.docx','docx','p22/d24/m_000074.docx','Т 1.9.docx','2026-01-30 06:56:21','2026-01-30 06:56:21');
INSERT INTO "methodical_materials" VALUES(75,'план','plan',NULL,'план 1.9.docx','m_000075.docx','p22/d24/m_000075.docx','docx','p22/d24/m_000075.docx','план 1.9.docx','2026-01-30 06:56:36','2026-01-30 06:56:36');
INSERT INTO "methodical_materials" VALUES(76,'план','plan',NULL,'план 1.10 ПРОЯВ.docx','m_000076.docx','p22/d24/m_000076.docx','docx','p22/d24/m_000076.docx','план 1.10 ПРОЯВ.docx','2026-01-30 06:56:59','2026-01-30 06:56:59');
INSERT INTO "methodical_materials" VALUES(77,'методичка','metod',NULL,'Т 1.10-(КС).docx','m_000077.docx','p22/d24/m_000077.docx','docx','p22/d24/m_000077.docx','Т 1.10-(КС).docx','2026-01-30 06:57:07','2026-01-30 06:57:07');
INSERT INTO "methodical_materials" VALUES(78,'план','plan',NULL,'ПЗ Т 1.11 стратегічні комунікації.docx','m_000078.docx','p22/d24/m_000078.docx','docx','p22/d24/m_000078.docx','ПЗ Т 1.11 стратегічні комунікації.docx','2026-01-30 06:57:34','2026-01-30 06:57:34');
INSERT INTO "methodical_materials" VALUES(79,'методичка','metod',NULL,'Т 1.11 - (ГЗ-3).docx','m_000079.docx','p22/d24/m_000079.docx','docx','p22/d24/m_000079.docx','Т 1.11 - (ГЗ-3).docx','2026-01-30 06:57:44','2026-01-30 06:57:44');
INSERT INTO "methodical_materials" VALUES(80,'план','plan',NULL,'план 1.12.docx','m_000080.docx','p22/d24/m_000080.docx','docx','p22/d24/m_000080.docx','план 1.12.docx','2026-01-30 06:58:11','2026-01-30 06:58:11');
INSERT INTO "methodical_materials" VALUES(81,'методичка','metod',NULL,'Т 1.12 Круглий стол L.docx','m_000081.docx','p22/d24/m_000081.docx','docx','p22/d24/m_000081.docx','Т 1.12 Круглий стол L.docx','2026-01-30 06:58:38','2026-01-30 06:58:38');
INSERT INTO "methodical_materials" VALUES(82,'план','plan',NULL,'План 1.13 ГЗ.docx','m_000082.docx','p22/d24/m_000082.docx','docx','p22/d24/m_000082.docx','План 1.13 ГЗ.docx','2026-01-30 06:58:55','2026-01-30 06:58:55');
INSERT INTO "methodical_materials" VALUES(83,'методичка','metod',NULL,'Т 1.13 ГЗ.docx','m_000083.docx','p22/d24/m_000083.docx','docx','p22/d24/m_000083.docx','Т 1.13 ГЗ.docx','2026-01-30 06:59:02','2026-01-30 06:59:02');
INSERT INTO "methodical_materials" VALUES(84,'Навчальний план-програма','attachment',NULL,'Шкло+духовність ПРАВКА.docx','m_000084.docx','p24/d25/m_000084.docx','docx','p24/d25/m_000084.docx','Шкло+духовність ПРАВКА.docx','2026-02-05 06:13:44','2026-02-05 06:13:44');
INSERT INTO "methodical_materials" VALUES(85,'методичка','metod',NULL,'метод 1.1. .docx','m_000085.docx','p24/d29/m_000085.docx','docx','p24/d29/m_000085.docx','метод 1.1. .docx','2026-02-05 06:52:33','2026-02-05 06:52:33');
INSERT INTO "methodical_materials" VALUES(86,'план','plan',NULL,'План_Т_1.1.docx','m_000086.docx','p24/d29/m_000086.docx','docx','p24/d29/m_000086.docx','План_Т_1.1.docx','2026-02-05 06:52:52','2026-02-05 06:52:52');
INSERT INTO "methodical_materials" VALUES(87,'презентація','presentation',NULL,'Т.1.1.pptx','m_000087.pptx','p24/d29/m_000087.pptx','pptx','p24/d29/m_000087.pptx','Т.1.1.pptx','2026-02-05 06:53:05','2026-02-05 06:53:05');
INSERT INTO "methodical_materials" VALUES(88,'Завдання для викладача','attachment',NULL,'Завдання для викладача на СР до Т 1.1 л.doc','m_000088.doc','p24/d29/m_000088.doc','doc','p24/d29/m_000088.doc','Завдання для викладача на СР до Т 1.1 л.doc','2026-02-05 06:53:28','2026-02-05 06:53:28');
INSERT INTO "methodical_materials" VALUES(89,'Завдання для курсантів','attachment',NULL,'Завдання для курсантів на СР до Т 1.1 л.doc','m_000089.doc','p24/d29/m_000089.doc','doc','p24/d29/m_000089.doc','Завдання для курсантів на СР до Т 1.1 л.doc','2026-02-05 06:53:41','2026-02-05 06:53:41');
INSERT INTO "methodical_materials" VALUES(90,'презентація','presentation',NULL,'1.2..pptx','m_000090.pptx','p24/d29/m_000090.pptx','pptx','p24/d29/m_000090.pptx','1.2..pptx','2026-02-05 06:54:05','2026-02-05 06:54:05');
INSERT INTO "methodical_materials" VALUES(91,'план','plan',NULL,'_План_Т_1.2.docx','m_000091.docx','p24/d29/m_000091.docx','docx','p24/d29/m_000091.docx','_План_Т_1.2.docx','2026-02-05 06:54:22','2026-02-05 06:54:22');
INSERT INTO "methodical_materials" VALUES(92,'методичка','metod',NULL,'метод 1.2. .docx','m_000092.docx','p24/d29/m_000092.docx','docx','p24/d29/m_000092.docx','метод 1.2. .docx','2026-02-05 06:54:40','2026-02-05 06:54:40');
INSERT INTO "methodical_materials" VALUES(93,'план','plan',NULL,'_План_Т_4.2 – копія.docx','m_000093.docx','p24/d29/m_000093.docx','docx','p24/d29/m_000093.docx','_План_Т_4.2 – копія.docx','2026-02-05 07:05:41','2026-02-05 07:05:41');
INSERT INTO "methodical_materials" VALUES(94,'методичка','metod',NULL,'_метод 4.2.docx','m_000094.docx','p24/d29/m_000094.docx','docx','p24/d29/m_000094.docx','_метод 4.2.docx','2026-02-05 07:05:56','2026-02-05 07:05:56');
INSERT INTO "methodical_materials" VALUES(95,'презентація','presentation',NULL,'4.2.pptx','m_000095.pptx','p24/d29/m_000095.pptx','pptx','p24/d29/m_000095.pptx','4.2.pptx','2026-02-05 07:06:07','2026-02-05 07:06:07');
INSERT INTO "methodical_materials" VALUES(96,'Завдання для викладача','attachment',NULL,'Завдання для викладача на СР до Т 4.1 л.doc','m_000096.doc','p24/d29/m_000096.doc','doc','p24/d29/m_000096.doc','Завдання для викладача на СР до Т 4.1 л.doc','2026-02-05 07:06:42','2026-02-05 07:06:42');
INSERT INTO "methodical_materials" VALUES(97,'Завдання для курсантів на','attachment',NULL,'Завдання для курсантів на СР до Т 4.1 л.doc','m_000097.doc','p24/d29/m_000097.doc','doc','p24/d29/m_000097.doc','Завдання для курсантів на СР до Т 4.1 л.doc','2026-02-05 07:06:57','2026-02-05 07:06:57');
INSERT INTO "methodical_materials" VALUES(98,'презентація','presentation',NULL,'4.1..pptx','m_000098.pptx','p24/d29/m_000098.pptx','pptx','p24/d29/m_000098.pptx','4.1..pptx','2026-02-05 07:07:12','2026-02-05 07:07:12');
INSERT INTO "methodical_materials" VALUES(99,'план','plan',NULL,'План_Т_4.1_гз.docx','m_000099.docx','p24/d29/m_000099.docx','docx','p24/d29/m_000099.docx','План_Т_4.1_гз.docx','2026-02-05 07:07:44','2026-02-05 07:07:44');
INSERT INTO "methodical_materials" VALUES(100,'методичка','metod',NULL,'4.1..pptx','m_000100.pptx','p24/d29/m_000100.pptx','pptx','p24/d29/m_000100.pptx','4.1..pptx','2026-02-05 07:07:57','2026-02-05 07:07:57');
INSERT INTO "methodical_materials" VALUES(101,'методичка','metod',NULL,'Історія 1 лекція Методичка.docx','m_000101.docx','p24/d29/m_000101.docx','docx','p24/d29/m_000101.docx','Історія 1 лекція Методичка.docx','2026-02-05 13:50:45','2026-02-05 13:50:45');
INSERT INTO "methodical_materials" VALUES(102,'план','plan',NULL,'Пл_Пр_Л_Т 2_1.docx','m_000102.docx','p24/d29/m_000102.docx','docx','p24/d29/m_000102.docx','Пл_Пр_Л_Т 2_1.docx','2026-02-05 13:50:55','2026-02-05 13:50:55');
INSERT INTO "methodical_materials" VALUES(103,'презентація','presentation',NULL,'преза шкло 1.pptm','m_000103.pptm','p24/d29/m_000103.pptm','pptm','p24/d29/m_000103.pptm','преза шкло 1.pptm','2026-02-05 13:52:08','2026-02-05 13:58:35');
INSERT INTO "methodical_materials" VALUES(104,'презентація','presentation',NULL,'преза шкло 2.pptm','m_000104.pptm','p24/d29/m_000104.pptm','pptm','p24/d29/m_000104.pptm','преза шкло 2.pptm','2026-02-05 13:54:32','2026-02-05 13:59:14');
INSERT INTO "methodical_materials" VALUES(105,'методичка','metod',NULL,'Історія 2 лекція меточка.docx','m_000105.docx','p24/d29/m_000105.docx','docx','p24/d29/m_000105.docx','Історія 2 лекція меточка.docx','2026-02-05 13:54:45','2026-02-05 13:59:30');
INSERT INTO "methodical_materials" VALUES(106,'план','plan',NULL,'Пл_Пр_Л_Т 2_2.docx','m_000106.docx','p24/d29/m_000106.docx','docx','p24/d29/m_000106.docx','Пл_Пр_Л_Т 2_2.docx','2026-02-05 13:54:55','2026-02-05 13:59:22');
INSERT INTO "methodical_materials" VALUES(107,'методичка','metod',NULL,'МПЗ  Т 3_1_ ГЗ.doc','m_000107.doc','p24/d29/m_000107.doc','doc','p24/d29/m_000107.doc','МПЗ  Т 3_1_ ГЗ.doc','2026-02-05 14:04:29','2026-02-05 14:04:29');
INSERT INTO "methodical_materials" VALUES(108,'план','plan',NULL,'План_Т_3.1_іл_Шкло.docx','m_000108.docx','p24/d29/m_000108.docx','docx','p24/d29/m_000108.docx','План_Т_3.1_іл_Шкло.docx','2026-02-05 14:04:47','2026-02-05 14:04:47');
INSERT INTO "methodical_materials" VALUES(109,'презентація','presentation',NULL,'ВК та ППП_Т 3.1 Шкло.pptx','m_000109.pptx','p24/d29/m_000109.pptx','pptx','p24/d29/m_000109.pptx','ВК та ППП_Т 3.1 Шкло.pptx','2026-02-05 14:05:01','2026-02-05 14:05:01');
INSERT INTO "methodical_materials" VALUES(110,'презентація','presentation',NULL,'ВК та_ППП_ Т 3.2 інформаційні навички додатково.pptx','m_000110.pptx','p24/d29/m_000110.pptx','pptx','p24/d29/m_000110.pptx','ВК та_ППП_ Т 3.2 інформаційні навички додатково.pptx','2026-02-05 14:05:21','2026-02-05 14:05:21');
INSERT INTO "methodical_materials" VALUES(111,'методичка','metod',NULL,'МПЗ  Т 3.2 Л_інформаційна гігієна.doc','m_000111.doc','p24/d29/m_000111.doc','doc','p24/d29/m_000111.doc','МПЗ  Т 3.2 Л_інформаційна гігієна.doc','2026-02-05 14:05:40','2026-02-05 14:05:40');
INSERT INTO "methodical_materials" VALUES(112,'план','plan',NULL,'План_Т_3.2_іл_Шкло.docx','m_000112.docx','p24/d29/m_000112.docx','docx','p24/d29/m_000112.docx','План_Т_3.2_іл_Шкло.docx','2026-02-05 14:05:57','2026-02-05 14:05:57');
INSERT INTO "methodical_materials" VALUES(113,'самостійна робота','attachment',NULL,'ВКта ППП  3 самостійна робота.docx','m_000113.docx','p24/d29/m_000113.docx','docx','p24/d29/m_000113.docx','ВКта ППП  3 самостійна робота.docx','2026-02-05 14:06:18','2026-02-05 14:06:18');
CREATE TABLE program_disciplines (
                    program_id INTEGER NOT NULL,
                    discipline_id INTEGER NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    PRIMARY KEY (program_id, discipline_id),
                    FOREIGN KEY (program_id) REFERENCES educational_programs(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
                        ON DELETE CASCADE
                );
INSERT INTO "program_disciplines" VALUES(22,24,1);
INSERT INTO "program_disciplines" VALUES(24,29,0);
CREATE TABLE program_topics (
                    program_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    PRIMARY KEY (program_id, topic_id),
                    FOREIGN KEY (program_id) REFERENCES educational_programs(id) 
                        ON DELETE CASCADE,
                    FOREIGN KEY (topic_id) REFERENCES topics(id) 
                        ON DELETE CASCADE
                );
CREATE VIRTUAL TABLE programs_fts USING fts5(
                    name, description, level,
                    content='educational_programs', content_rowid='id'
                );
INSERT INTO "programs_fts" VALUES('L1C ЗЕВТ МАГІСТРИ 2025',NULL,'L1C');
INSERT INTO "programs_fts" VALUES('ДКЛ 2025','Додаткового курсу лідерства зі здобувачами освіти, щодо розвитку моральних, 
інтелектуальних та психологічних компетенцій майбутніх офіцерів.',NULL);
CREATE TABLE questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    answer TEXT,
                    difficulty_level INTEGER DEFAULT 1,
                    order_index INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
INSERT INTO "questions" VALUES(1604,'1.  Сутність та зміст ціннісних теорій лідерства.',NULL,1,1,'2026-01-29 11:32:44','2026-01-29 11:48:19');
INSERT INTO "questions" VALUES(1605,'2. Ціннісні аспекти лідерства для професійної підготовки військових фахівців',NULL,1,2,'2026-01-29 11:32:44','2026-01-29 11:48:52');
INSERT INTO "questions" VALUES(1606,'1. Гендерна рівність в секторі безпеки і оборони України.',NULL,1,1,'2026-01-29 11:32:44','2026-01-29 11:50:39');
INSERT INTO "questions" VALUES(1607,'2. Гендерна компетентність як складова професійної компетентності офіцера.',NULL,1,2,'2026-01-29 11:32:44','2026-01-29 11:50:42');
INSERT INTO "questions" VALUES(1608,'1.  Авторитет і лідерство командира (начальника).',NULL,1,3,'2026-01-29 11:32:44','2026-01-29 11:52:28');
INSERT INTO "questions" VALUES(1609,'2. Основи формування професіоналізму і лідерства офіцерського складу.',NULL,1,4,'2026-01-29 11:32:44','2026-01-29 11:52:45');
INSERT INTO "questions" VALUES(1610,'1. Теоретичні засади управління.',NULL,1,1,'2026-01-29 11:32:44','2026-01-29 11:53:46');
INSERT INTO "questions" VALUES(1611,'2. Загальні функції управління.',NULL,1,2,'2026-01-29 11:32:44','2026-01-29 11:54:00');
INSERT INTO "questions" VALUES(1613,'1. Система особистих якостей керівника.','',1,1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1614,'2. Організаційна культура керівника.','',1,2,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1615,'3. Етичні проблеми управління.','',1,3,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1618,'1. Форми управлінського впливу.','',1,1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1619,'2. Класифікація стилів керівництва.','',1,2,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1620,'3. Ситуаційний і адаптивний підхід до ефективного лідерства. «Лідерство» за стандартами НАТО.','',1,3,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1621,'4. Взаємодія командира (начальника) з підлеглим.','',1,4,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1624,'1. Сутність та зміст процесу комунікації в управлінні.','',1,1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1625,'2. Військовий колектив і стадії його розвитку.','',1,2,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1626,'3. Психологічні та ділові особливості підлеглих.','',1,3,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1629,'1. Теоретичні основи та ситуаційне лідерство в діяльності командира підрозділу.','',1,1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1630,'2. Досвід використання теорії ситуаційного лідерства в професійній діяльності офіцера.','',1,2,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1633,'1. Суть, характеристика проявів девіантної поведінки на війні.','',1,1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1634,'2. Форми та методи соціально-психологічної релаксації та реабілітації військовослужбовців.','',1,2,'2026-01-29 11:32:44','2026-01-29 14:15:54');
INSERT INTO "questions" VALUES(1637,'1. Перегляд відеофільму “Висота 307,5”.','',1,1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1638,'2. Обговорення дій командира (начальника) та солдат, які позитивно впливають на імідж Збройних Сил України.','',1,2,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1639,'3. Обговорення негативних дій командирів та солдат під час участі у бойових діях.','',1,3,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1642,'1. Інформаційна гігієна військ.','',1,1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1643,'2. Вивчення проблем стратегічних комунікацій в Збройних Силах України.','',1,2,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1646,'1. Поняття психологічного здоров’я та профілактика психологічних відхилень.','',1,1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1647,'2. Народні традиції та проблема глобалізації; традиції як чинник психологічного здоров’я.','',1,2,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1650,'1. Обмеження загального характеру ведення війни.','',1,1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1651,'2. Заборонені методи та способи ведення війни.','',1,2,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1652,'3. Застосування зброї військовослужбовцями з метою захисту здоров’я і життя, відбиття нападу на військові об’єкти.','',1,3,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1655,'1. Практичне рішення контрольного завдання за навчальну дисципліну.','',1,1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "questions" VALUES(1656,'3. Роль командира (начальника) у забезпеченні рівних прав та можливостей чоловіків та жінок.',NULL,1,3,'2026-01-29 11:50:22','2026-01-29 11:50:35');
INSERT INTO "questions" VALUES(1657,'3. Методи управління.',NULL,1,3,'2026-01-29 11:55:27','2026-01-29 11:55:27');
INSERT INTO "questions" VALUES(1658,'1. Честь, єдність, стійкість, професійність.',NULL,1,1,'2026-02-05 06:47:04','2026-02-05 06:47:04');
INSERT INTO "questions" VALUES(1659,'2. Правила взаємодії в команді. Мета, місія підрозділу.',NULL,1,2,'2026-02-05 06:47:16','2026-02-05 06:47:16');
INSERT INTO "questions" VALUES(1660,'3. П’ять вад роботи команди за Патріком Ленсіоні.',NULL,1,3,'2026-02-05 06:47:26','2026-02-05 06:47:26');
INSERT INTO "questions" VALUES(1664,'1. Самопрезентація військовослужбовця.',NULL,1,1,'2026-02-05 06:51:58','2026-02-05 06:51:58');
INSERT INTO "questions" VALUES(1665,'1. Нормативні вимоги в Збройних Силах України щодо забезпечення духовно-релігійних потреб особового складу: «Служити своїм, сприяти іншим, опікуватись усіма».',NULL,1,1,'2026-02-05 07:04:27','2026-02-05 07:04:27');
INSERT INTO "questions" VALUES(1666,'2. Використання душпастирської опіки як недооціненого ресурсу щодо формування морального авторитету військовослужбовців.',NULL,1,2,'2026-02-05 07:04:35','2026-02-05 07:04:35');
INSERT INTO "questions" VALUES(1667,'3. Забезпечення командиром задоволення соціальних та духовних потреб особового складу.',NULL,1,3,'2026-02-05 07:04:41','2026-02-05 07:04:41');
INSERT INTO "questions" VALUES(1668,'4. Ефективна інтеграція душпастирської функції та формування довіри серед особового складу.',NULL,1,4,'2026-02-05 07:04:55','2026-02-05 07:04:55');
INSERT INTO "questions" VALUES(1669,'1. Тестування особового складу.',NULL,1,1,'2026-02-05 07:05:18','2026-02-05 07:05:18');
INSERT INTO "questions" VALUES(1674,'1. Актуальність формування та впровадження військових традицій.',NULL,1,0,'2026-02-05 13:49:24','2026-02-05 13:49:24');
INSERT INTO "questions" VALUES(1675,'2. Основні засади формування військових традицій.',NULL,1,0,'2026-02-05 13:49:35','2026-02-05 13:49:35');
INSERT INTO "questions" VALUES(1676,'3. Непритаманні традиції в Українському війську: призма історії (татуювання, неонацизм).',NULL,1,0,'2026-02-05 13:49:42','2026-02-05 13:49:42');
INSERT INTO "questions" VALUES(1677,'4. Сучасний стан військових традицій та ритуалів.',NULL,1,0,'2026-02-05 13:49:51','2026-02-05 13:49:51');
INSERT INTO "questions" VALUES(1678,'1. Воїни що творили державу – від Русі до Гетьманщини.',NULL,1,1,'2026-02-05 13:53:56','2026-02-05 13:53:56');
INSERT INTO "questions" VALUES(1679,'2. Українська революція 1917-1921 рр.',NULL,1,2,'2026-02-05 13:53:56','2026-02-05 13:53:56');
INSERT INTO "questions" VALUES(1680,'1. Особисті якості майбутніх офіцерів, які визначають вплив на мотивацію та поведінку особового складу.',NULL,1,1,'2026-02-05 14:00:49','2026-02-05 14:00:49');
INSERT INTO "questions" VALUES(1681,'2. Якісний моральний і психологічний вплив командирів по згуртуванню колективу.',NULL,1,2,'2026-02-05 14:00:49','2026-02-05 14:00:49');
INSERT INTO "questions" VALUES(1682,'3. Профілактика девіантної поведінки в підрозділах.',NULL,1,3,'2026-02-05 14:00:49','2026-02-05 14:00:49');
INSERT INTO "questions" VALUES(1683,'1. Імідж ВВНЗ та ЗС України: ознаки та наслідки негативного впливу.',NULL,1,1,'2026-02-05 14:01:47','2026-02-05 14:01:47');
INSERT INTO "questions" VALUES(1684,'2. Оцінювання інформаційного середовища: виявлення, аналіз та прогнозування потенційних інформаційних загроз.',NULL,1,2,'2026-02-05 14:01:47','2026-02-05 14:01:47');
CREATE VIRTUAL TABLE questions_fts USING fts5(
                    content, answer,
                    content='questions', content_rowid='id'
                );
INSERT INTO "questions_fts" VALUES('1.  Сутність та зміст ціннісних теорій лідерства.',NULL);
INSERT INTO "questions_fts" VALUES('2. Ціннісні аспекти лідерства для професійної підготовки військових фахівців',NULL);
INSERT INTO "questions_fts" VALUES('1. Гендерна рівність в секторі безпеки і оборони України.',NULL);
INSERT INTO "questions_fts" VALUES('2. Гендерна компетентність як складова професійної компетентності офіцера.',NULL);
INSERT INTO "questions_fts" VALUES('1.  Авторитет і лідерство командира (начальника).',NULL);
INSERT INTO "questions_fts" VALUES('2. Основи формування професіоналізму і лідерства офіцерського складу.',NULL);
INSERT INTO "questions_fts" VALUES('1. Теоретичні засади управління.',NULL);
INSERT INTO "questions_fts" VALUES('2. Загальні функції управління.',NULL);
INSERT INTO "questions_fts" VALUES('1. Система особистих якостей керівника.','');
INSERT INTO "questions_fts" VALUES('2. Організаційна культура керівника.','');
INSERT INTO "questions_fts" VALUES('3. Етичні проблеми управління.','');
INSERT INTO "questions_fts" VALUES('1. Форми управлінського впливу.','');
INSERT INTO "questions_fts" VALUES('2. Класифікація стилів керівництва.','');
INSERT INTO "questions_fts" VALUES('3. Ситуаційний і адаптивний підхід до ефективного лідерства. «Лідерство» за стандартами НАТО.','');
INSERT INTO "questions_fts" VALUES('4. Взаємодія командира (начальника) з підлеглим.','');
INSERT INTO "questions_fts" VALUES('1. Сутність та зміст процесу комунікації в управлінні.','');
INSERT INTO "questions_fts" VALUES('2. Військовий колектив і стадії його розвитку.','');
INSERT INTO "questions_fts" VALUES('3. Психологічні та ділові особливості підлеглих.','');
INSERT INTO "questions_fts" VALUES('1. Теоретичні основи та ситуаційне лідерство в діяльності командира підрозділу.','');
INSERT INTO "questions_fts" VALUES('2. Досвід використання теорії ситуаційного лідерства в професійній діяльності офіцера.','');
INSERT INTO "questions_fts" VALUES('1. Суть, характеристика проявів девіантної поведінки на війні.','');
INSERT INTO "questions_fts" VALUES('2. Форми та методи соціально-психологічної релаксації та реабілітації військовослужбовців.','');
INSERT INTO "questions_fts" VALUES('1. Перегляд відеофільму “Висота 307,5”.','');
INSERT INTO "questions_fts" VALUES('2. Обговорення дій командира (начальника) та солдат, які позитивно впливають на імідж Збройних Сил України.','');
INSERT INTO "questions_fts" VALUES('3. Обговорення негативних дій командирів та солдат під час участі у бойових діях.','');
INSERT INTO "questions_fts" VALUES('1. Інформаційна гігієна військ.','');
INSERT INTO "questions_fts" VALUES('2. Вивчення проблем стратегічних комунікацій в Збройних Силах України.','');
INSERT INTO "questions_fts" VALUES('1. Поняття психологічного здоров’я та профілактика психологічних відхилень.','');
INSERT INTO "questions_fts" VALUES('2. Народні традиції та проблема глобалізації; традиції як чинник психологічного здоров’я.','');
INSERT INTO "questions_fts" VALUES('1. Обмеження загального характеру ведення війни.','');
INSERT INTO "questions_fts" VALUES('2. Заборонені методи та способи ведення війни.','');
INSERT INTO "questions_fts" VALUES('3. Застосування зброї військовослужбовцями з метою захисту здоров’я і життя, відбиття нападу на військові об’єкти.','');
INSERT INTO "questions_fts" VALUES('1. Практичне рішення контрольного завдання за навчальну дисципліну.','');
INSERT INTO "questions_fts" VALUES('3. Роль командира (начальника) у забезпеченні рівних прав та можливостей чоловіків та жінок.',NULL);
INSERT INTO "questions_fts" VALUES('3. Методи управління.',NULL);
INSERT INTO "questions_fts" VALUES('1. Честь, єдність, стійкість, професійність.',NULL);
INSERT INTO "questions_fts" VALUES('2. Правила взаємодії в команді. Мета, місія підрозділу.',NULL);
INSERT INTO "questions_fts" VALUES('3. П’ять вад роботи команди за Патріком Ленсіоні.',NULL);
INSERT INTO "questions_fts" VALUES('1. Самопрезентація військовослужбовця.',NULL);
INSERT INTO "questions_fts" VALUES('1. Нормативні вимоги в Збройних Силах України щодо забезпечення духовно-релігійних потреб особового складу: «Служити своїм, сприяти іншим, опікуватись усіма».',NULL);
INSERT INTO "questions_fts" VALUES('2. Використання душпастирської опіки як недооціненого ресурсу щодо формування морального авторитету військовослужбовців.',NULL);
INSERT INTO "questions_fts" VALUES('3. Забезпечення командиром задоволення соціальних та духовних потреб особового складу.',NULL);
INSERT INTO "questions_fts" VALUES('4. Ефективна інтеграція душпастирської функції та формування довіри серед особового складу.',NULL);
INSERT INTO "questions_fts" VALUES('1. Тестування особового складу.',NULL);
INSERT INTO "questions_fts" VALUES('1. Актуальність формування та впровадження військових традицій.',NULL);
INSERT INTO "questions_fts" VALUES('2. Основні засади формування військових традицій.',NULL);
INSERT INTO "questions_fts" VALUES('3. Непритаманні традиції в Українському війську: призма історії (татуювання, неонацизм).',NULL);
INSERT INTO "questions_fts" VALUES('4. Сучасний стан військових традицій та ритуалів.',NULL);
INSERT INTO "questions_fts" VALUES('1. Воїни що творили державу – від Русі до Гетьманщини.',NULL);
INSERT INTO "questions_fts" VALUES('2. Українська революція 1917-1921 рр.',NULL);
INSERT INTO "questions_fts" VALUES('1. Особисті якості майбутніх офіцерів, які визначають вплив на мотивацію та поведінку особового складу.',NULL);
INSERT INTO "questions_fts" VALUES('2. Якісний моральний і психологічний вплив командирів по згуртуванню колективу.',NULL);
INSERT INTO "questions_fts" VALUES('3. Профілактика девіантної поведінки в підрозділах.',NULL);
INSERT INTO "questions_fts" VALUES('1. Імідж ВВНЗ та ЗС України: ознаки та наслідки негативного впливу.',NULL);
INSERT INTO "questions_fts" VALUES('2. Оцінювання інформаційного середовища: виявлення, аналіз та прогнозування потенційних інформаційних загроз.',NULL);
CREATE TABLE schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL
            );
INSERT INTO "schema_migrations" VALUES(1,2);
INSERT INTO "schema_migrations" VALUES(2,3);
INSERT INTO "schema_migrations" VALUES(3,4);
INSERT INTO "schema_migrations" VALUES(4,5);
INSERT INTO "schema_migrations" VALUES(5,6);
INSERT INTO "schema_migrations" VALUES(6,7);
INSERT INTO "schema_migrations" VALUES(7,8);
INSERT INTO "schema_migrations" VALUES(8,9);
INSERT INTO "schema_migrations" VALUES(9,10);
CREATE TABLE teacher_disciplines (
                    teacher_id INTEGER NOT NULL,
                    discipline_id INTEGER NOT NULL,
                    PRIMARY KEY (teacher_id, discipline_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
                        ON DELETE CASCADE
                );
INSERT INTO "teacher_disciplines" VALUES(28,24);
INSERT INTO "teacher_disciplines" VALUES(21,24);
INSERT INTO "teacher_disciplines" VALUES(30,24);
INSERT INTO "teacher_disciplines" VALUES(34,24);
INSERT INTO "teacher_disciplines" VALUES(22,24);
INSERT INTO "teacher_disciplines" VALUES(26,24);
INSERT INTO "teacher_disciplines" VALUES(34,29);
INSERT INTO "teacher_disciplines" VALUES(28,29);
INSERT INTO "teacher_disciplines" VALUES(32,29);
CREATE TABLE teacher_materials (
                    teacher_id INTEGER NOT NULL,
                    material_id INTEGER NOT NULL,
                    role TEXT DEFAULT 'author',
                    PRIMARY KEY (teacher_id, material_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id) 
                        ON DELETE CASCADE,
                    FOREIGN KEY (material_id) REFERENCES methodical_materials(id) 
                        ON DELETE CASCADE
                );
INSERT INTO "teacher_materials" VALUES(34,7,'author');
INSERT INTO "teacher_materials" VALUES(34,6,'author');
INSERT INTO "teacher_materials" VALUES(34,5,'author');
INSERT INTO "teacher_materials" VALUES(27,8,'author');
INSERT INTO "teacher_materials" VALUES(34,9,'author');
INSERT INTO "teacher_materials" VALUES(34,10,'author');
INSERT INTO "teacher_materials" VALUES(34,11,'author');
INSERT INTO "teacher_materials" VALUES(30,12,'author');
INSERT INTO "teacher_materials" VALUES(30,13,'author');
INSERT INTO "teacher_materials" VALUES(30,15,'author');
INSERT INTO "teacher_materials" VALUES(30,16,'author');
INSERT INTO "teacher_materials" VALUES(30,17,'author');
INSERT INTO "teacher_materials" VALUES(30,19,'author');
INSERT INTO "teacher_materials" VALUES(30,23,'author');
INSERT INTO "teacher_materials" VALUES(30,24,'author');
INSERT INTO "teacher_materials" VALUES(30,25,'author');
INSERT INTO "teacher_materials" VALUES(30,26,'author');
INSERT INTO "teacher_materials" VALUES(30,27,'author');
INSERT INTO "teacher_materials" VALUES(30,28,'author');
INSERT INTO "teacher_materials" VALUES(30,29,'author');
INSERT INTO "teacher_materials" VALUES(30,30,'author');
INSERT INTO "teacher_materials" VALUES(30,31,'author');
INSERT INTO "teacher_materials" VALUES(30,32,'author');
INSERT INTO "teacher_materials" VALUES(30,33,'author');
INSERT INTO "teacher_materials" VALUES(30,35,'author');
INSERT INTO "teacher_materials" VALUES(30,36,'author');
INSERT INTO "teacher_materials" VALUES(30,37,'author');
INSERT INTO "teacher_materials" VALUES(30,38,'author');
INSERT INTO "teacher_materials" VALUES(30,39,'author');
INSERT INTO "teacher_materials" VALUES(30,40,'author');
INSERT INTO "teacher_materials" VALUES(30,41,'author');
INSERT INTO "teacher_materials" VALUES(30,42,'author');
INSERT INTO "teacher_materials" VALUES(30,43,'author');
INSERT INTO "teacher_materials" VALUES(30,46,'author');
INSERT INTO "teacher_materials" VALUES(30,47,'author');
INSERT INTO "teacher_materials" VALUES(30,48,'author');
INSERT INTO "teacher_materials" VALUES(30,49,'author');
INSERT INTO "teacher_materials" VALUES(34,50,'author');
INSERT INTO "teacher_materials" VALUES(34,51,'author');
INSERT INTO "teacher_materials" VALUES(34,52,'author');
INSERT INTO "teacher_materials" VALUES(34,53,'author');
INSERT INTO "teacher_materials" VALUES(34,54,'author');
INSERT INTO "teacher_materials" VALUES(34,55,'author');
INSERT INTO "teacher_materials" VALUES(34,56,'author');
INSERT INTO "teacher_materials" VALUES(34,57,'author');
INSERT INTO "teacher_materials" VALUES(34,58,'author');
INSERT INTO "teacher_materials" VALUES(34,59,'author');
INSERT INTO "teacher_materials" VALUES(34,60,'author');
INSERT INTO "teacher_materials" VALUES(34,61,'author');
INSERT INTO "teacher_materials" VALUES(34,62,'author');
INSERT INTO "teacher_materials" VALUES(34,63,'author');
INSERT INTO "teacher_materials" VALUES(34,64,'author');
INSERT INTO "teacher_materials" VALUES(34,65,'author');
INSERT INTO "teacher_materials" VALUES(34,66,'author');
INSERT INTO "teacher_materials" VALUES(30,14,'author');
INSERT INTO "teacher_materials" VALUES(34,18,'author');
INSERT INTO "teacher_materials" VALUES(34,22,'author');
INSERT INTO "teacher_materials" VALUES(34,21,'author');
INSERT INTO "teacher_materials" VALUES(34,67,'author');
INSERT INTO "teacher_materials" VALUES(34,68,'author');
INSERT INTO "teacher_materials" VALUES(34,69,'author');
INSERT INTO "teacher_materials" VALUES(34,70,'author');
INSERT INTO "teacher_materials" VALUES(34,71,'author');
INSERT INTO "teacher_materials" VALUES(34,72,'author');
INSERT INTO "teacher_materials" VALUES(34,73,'author');
INSERT INTO "teacher_materials" VALUES(34,74,'author');
INSERT INTO "teacher_materials" VALUES(30,34,'author');
INSERT INTO "teacher_materials" VALUES(34,75,'author');
INSERT INTO "teacher_materials" VALUES(34,76,'author');
INSERT INTO "teacher_materials" VALUES(34,77,'author');
INSERT INTO "teacher_materials" VALUES(34,78,'author');
INSERT INTO "teacher_materials" VALUES(34,79,'author');
INSERT INTO "teacher_materials" VALUES(34,80,'author');
INSERT INTO "teacher_materials" VALUES(34,81,'author');
INSERT INTO "teacher_materials" VALUES(34,82,'author');
INSERT INTO "teacher_materials" VALUES(34,83,'author');
INSERT INTO "teacher_materials" VALUES(34,84,'author');
INSERT INTO "teacher_materials" VALUES(21,84,'author');
INSERT INTO "teacher_materials" VALUES(34,85,'author');
INSERT INTO "teacher_materials" VALUES(34,86,'author');
INSERT INTO "teacher_materials" VALUES(34,87,'author');
INSERT INTO "teacher_materials" VALUES(34,88,'author');
INSERT INTO "teacher_materials" VALUES(34,89,'author');
INSERT INTO "teacher_materials" VALUES(34,90,'author');
INSERT INTO "teacher_materials" VALUES(34,91,'author');
INSERT INTO "teacher_materials" VALUES(34,92,'author');
INSERT INTO "teacher_materials" VALUES(34,93,'author');
INSERT INTO "teacher_materials" VALUES(34,94,'author');
INSERT INTO "teacher_materials" VALUES(34,95,'author');
INSERT INTO "teacher_materials" VALUES(34,96,'author');
INSERT INTO "teacher_materials" VALUES(34,97,'author');
INSERT INTO "teacher_materials" VALUES(34,98,'author');
INSERT INTO "teacher_materials" VALUES(34,99,'author');
INSERT INTO "teacher_materials" VALUES(34,100,'author');
INSERT INTO "teacher_materials" VALUES(28,101,'author');
INSERT INTO "teacher_materials" VALUES(28,102,'author');
INSERT INTO "teacher_materials" VALUES(28,104,'author');
INSERT INTO "teacher_materials" VALUES(28,105,'author');
INSERT INTO "teacher_materials" VALUES(28,106,'author');
INSERT INTO "teacher_materials" VALUES(32,107,'author');
INSERT INTO "teacher_materials" VALUES(32,108,'author');
INSERT INTO "teacher_materials" VALUES(32,109,'author');
INSERT INTO "teacher_materials" VALUES(32,110,'author');
INSERT INTO "teacher_materials" VALUES(32,111,'author');
INSERT INTO "teacher_materials" VALUES(32,112,'author');
INSERT INTO "teacher_materials" VALUES(32,113,'author');
CREATE TABLE teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    position TEXT,
                    department TEXT,
                    email TEXT,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                , military_rank TEXT);
INSERT INTO "teachers" VALUES(21,'РОЩЕНКОВ Тарас Олександрович','Начальник кафедри','РОЩЕНКОВ Тарас Олександрович','0675909293','kudalik111@gmail.com','2026-01-28 07:32:41','2026-01-28 07:32:41','полковник');
INSERT INTO "teachers" VALUES(22,'ЦИМБАЛ Михайло Романович','Заступник начальника кафедри','ЦИМБАЛ Михайло Романович','0975937074','mishava1105@ukr.net','2026-01-28 07:32:41','2026-01-28 07:32:41','підполковник');
INSERT INTO "teachers" VALUES(23,'КОРДІЯКА Юрій Миколайович','Старший викладач','КОРДІЯКА Юрій Миколайович','0675170624',NULL,'2026-01-28 07:32:41','2026-01-28 07:32:41','полковник');
INSERT INTO "teachers" VALUES(24,'ШУТ Василь Олександрович','Старший викладач','ШУТ Василь Олександрович','0677377582','WasylSchut@gmail.com','2026-01-28 07:32:41','2026-01-28 07:32:41','підполковник');
INSERT INTO "teachers" VALUES(25,'ПАЛЯСНИЙ Віктор Петрович','Старший викладач','ПАЛЯСНИЙ Віктор Петрович','0632815141','palyasnij@ukr.net','2026-01-28 07:32:41','2026-01-28 07:32:41','підполковник');
INSERT INTO "teachers" VALUES(26,'ОДИНЦОВА Ольга Ігорівна','Старший викладач','ОДИНЦОВА Ольга Ігорівна','0632737727','od1504@ukr.net','2026-01-28 07:32:41','2026-01-28 07:32:41','підполковник');
INSERT INTO "teachers" VALUES(27,'КНІШ Марія Ігорівна','Старший викладач','КНІШ Марія Ігорівна','0632624588','mariya.yalanskaya@gmail.com','2026-01-28 07:32:41','2026-01-28 07:32:41','підполковник');
INSERT INTO "teachers" VALUES(28,'ШКАРПИЦЬКИЙ Віталій Михайлович','Викладач','ШКАРПИЦЬКИЙ Віталій Михайлович','0939883530','vetal2621982@gmail.com','2026-01-28 07:32:41','2026-01-28 07:32:41','підполковник');
INSERT INTO "teachers" VALUES(29,'БОРИСОВА Світлана Борисівна','Викладач','БОРИСОВА Світлана Борисівна','0631837370','oda82000@gmail.com','2026-01-28 07:32:41','2026-01-28 07:32:41','підполковник');
INSERT INTO "teachers" VALUES(30,'САВЧУК Віталій Олександрович','Викладач','САВЧУК Віталій Олександрович','0961700928','savhcukv@gmail.com','2026-01-28 07:32:41','2026-01-28 07:32:41','майор');
INSERT INTO "teachers" VALUES(31,'ЗИЗА Микола Миколайович','Викладач','ЗИЗА Микола Миколайович','0509541290','zyza.nikolay@meta.ua','2026-01-28 07:32:41','2026-01-28 07:32:41','підполковник');
INSERT INTO "teachers" VALUES(32,'ГРАЧОВА Альона Миколаївна','Викладач','ГРАЧОВА Альона Миколаївна','0668970230','shuravell@ukr.net','2026-01-28 07:32:41','2026-01-28 07:32:41','майор');
INSERT INTO "teachers" VALUES(33,'ПОЛІЩУК Володимир Андрійович','Викладач','ПОЛІЩУК Володимир Андрійович','0972693585','vpol1977@gmail.com','2026-01-28 07:32:41','2026-01-28 07:32:41','старший лейтенант');
INSERT INTO "teachers" VALUES(34,'ФИЛИПОВИЧ Георгій Данилович','Викладач','ФИЛИПОВИЧ Георгій Данилович','0936227538','red.ukr@gmail.com','2026-01-28 07:32:41','2026-01-28 07:32:41','лейтенант');
INSERT INTO "teachers" VALUES(35,'МУНТЯН Борис Іванович','Доцент','МУНТЯН Борис Іванович','0972478878','bobmuntian2018@ukr.net','2026-01-28 07:32:41','2026-01-28 07:32:41','працівник ЗСУ');
INSERT INTO "teachers" VALUES(36,'РОЗМАЗНІН Олександр Петрович','Доцент','РОЗМАЗНІН Олександр Петрович','0677514713','rozmaznin@gmail.com','2026-01-28 07:32:41','2026-01-28 07:32:41','працівник ЗСУ');
INSERT INTO "teachers" VALUES(37,'ГЛАДЧЕНКО Світлана Володимирівна','Доцент','ГЛАДЧЕНКО Світлана Володимирівна','0677524088','vessta_odessa@ukr.net','2026-01-28 07:32:41','2026-01-28 07:32:41','працівник ЗСУ');
CREATE VIRTUAL TABLE teachers_fts USING fts5(
                full_name, military_rank, position, department, email,
                content='teachers', content_rowid='id'
            );
INSERT INTO "teachers_fts" VALUES('РОЩЕНКОВ Тарас Олександрович','полковник','Начальник кафедри','РОЩЕНКОВ Тарас Олександрович','0675909293');
INSERT INTO "teachers_fts" VALUES('ЦИМБАЛ Михайло Романович','підполковник','Заступник начальника кафедри','ЦИМБАЛ Михайло Романович','0975937074');
INSERT INTO "teachers_fts" VALUES('КОРДІЯКА Юрій Миколайович','полковник','Старший викладач','КОРДІЯКА Юрій Миколайович','0675170624');
INSERT INTO "teachers_fts" VALUES('ШУТ Василь Олександрович','підполковник','Старший викладач','ШУТ Василь Олександрович','0677377582');
INSERT INTO "teachers_fts" VALUES('ПАЛЯСНИЙ Віктор Петрович','підполковник','Старший викладач','ПАЛЯСНИЙ Віктор Петрович','0632815141');
INSERT INTO "teachers_fts" VALUES('ОДИНЦОВА Ольга Ігорівна','підполковник','Старший викладач','ОДИНЦОВА Ольга Ігорівна','0632737727');
INSERT INTO "teachers_fts" VALUES('КНІШ Марія Ігорівна','підполковник','Старший викладач','КНІШ Марія Ігорівна','0632624588');
INSERT INTO "teachers_fts" VALUES('ШКАРПИЦЬКИЙ Віталій Михайлович','підполковник','Викладач','ШКАРПИЦЬКИЙ Віталій Михайлович','0939883530');
INSERT INTO "teachers_fts" VALUES('БОРИСОВА Світлана Борисівна','підполковник','Викладач','БОРИСОВА Світлана Борисівна','0631837370');
INSERT INTO "teachers_fts" VALUES('САВЧУК Віталій Олександрович','майор','Викладач','САВЧУК Віталій Олександрович','0961700928');
INSERT INTO "teachers_fts" VALUES('ЗИЗА Микола Миколайович','підполковник','Викладач','ЗИЗА Микола Миколайович','0509541290');
INSERT INTO "teachers_fts" VALUES('ГРАЧОВА Альона Миколаївна','майор','Викладач','ГРАЧОВА Альона Миколаївна','0668970230');
INSERT INTO "teachers_fts" VALUES('ПОЛІЩУК Володимир Андрійович','старший лейтенант','Викладач','ПОЛІЩУК Володимир Андрійович','0972693585');
INSERT INTO "teachers_fts" VALUES('ФИЛИПОВИЧ Георгій Данилович','лейтенант','Викладач','ФИЛИПОВИЧ Георгій Данилович','0936227538');
INSERT INTO "teachers_fts" VALUES('МУНТЯН Борис Іванович','працівник ЗСУ','Доцент','МУНТЯН Борис Іванович','0972478878');
INSERT INTO "teachers_fts" VALUES('РОЗМАЗНІН Олександр Петрович','працівник ЗСУ','Доцент','РОЗМАЗНІН Олександр Петрович','0677514713');
INSERT INTO "teachers_fts" VALUES('ГЛАДЧЕНКО Світлана Володимирівна','працівник ЗСУ','Доцент','ГЛАДЧЕНКО Світлана Володимирівна','0677524088');
CREATE TABLE topic_lessons (
                    topic_id INTEGER NOT NULL,
                    lesson_id INTEGER NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    PRIMARY KEY (topic_id, lesson_id),
                    FOREIGN KEY (topic_id) REFERENCES topics(id) 
                        ON DELETE CASCADE,
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id) 
                        ON DELETE CASCADE
                );
INSERT INTO "topic_lessons" VALUES(61,589,1);
INSERT INTO "topic_lessons" VALUES(61,591,2);
INSERT INTO "topic_lessons" VALUES(61,593,3);
INSERT INTO "topic_lessons" VALUES(61,594,4);
INSERT INTO "topic_lessons" VALUES(61,595,5);
INSERT INTO "topic_lessons" VALUES(61,596,6);
INSERT INTO "topic_lessons" VALUES(61,598,7);
INSERT INTO "topic_lessons" VALUES(61,599,8);
INSERT INTO "topic_lessons" VALUES(61,600,9);
INSERT INTO "topic_lessons" VALUES(61,601,10);
INSERT INTO "topic_lessons" VALUES(61,602,11);
INSERT INTO "topic_lessons" VALUES(61,603,12);
INSERT INTO "topic_lessons" VALUES(61,604,14);
INSERT INTO "topic_lessons" VALUES(61,605,14);
INSERT INTO "topic_lessons" VALUES(62,606,1);
INSERT INTO "topic_lessons" VALUES(62,607,2);
INSERT INTO "topic_lessons" VALUES(62,608,3);
INSERT INTO "topic_lessons" VALUES(65,609,1);
INSERT INTO "topic_lessons" VALUES(65,610,2);
INSERT INTO "topic_lessons" VALUES(65,611,3);
INSERT INTO "topic_lessons" VALUES(63,615,1);
INSERT INTO "topic_lessons" VALUES(63,616,3);
INSERT INTO "topic_lessons" VALUES(63,617,2);
INSERT INTO "topic_lessons" VALUES(64,618,1);
INSERT INTO "topic_lessons" VALUES(64,619,2);
INSERT INTO "topic_lessons" VALUES(64,620,3);
CREATE TABLE topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    order_index INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
INSERT INTO "topics" VALUES(61,'Тема 1. Лідерство','',1,'2026-01-29 11:32:44','2026-01-29 11:32:44');
INSERT INTO "topics" VALUES(62,'Військове лідерство',NULL,1,'2026-02-05 06:43:48','2026-02-05 06:43:48');
INSERT INTO "topics" VALUES(63,'Історія військових традицій України',NULL,2,'2026-02-05 06:44:09','2026-02-05 06:44:39');
INSERT INTO "topics" VALUES(64,'Внутрішні комунікації та психологічна підтримка персоналу',NULL,3,'2026-02-05 06:44:15','2026-02-05 06:44:15');
INSERT INTO "topics" VALUES(65,'Духовне лідерство та морально-ціннісна стійкість у ЗС України',NULL,4,'2026-02-05 06:44:22','2026-02-05 06:44:22');
CREATE VIRTUAL TABLE topics_fts USING fts5(
                    title, description,
                    content='topics', content_rowid='id'
                );
INSERT INTO "topics_fts" VALUES('Тема 1. Лідерство','');
INSERT INTO "topics_fts" VALUES('Військове лідерство',NULL);
INSERT INTO "topics_fts" VALUES('Історія військових традицій України',NULL);
INSERT INTO "topics_fts" VALUES('Внутрішні комунікації та психологічна підтримка персоналу',NULL);
INSERT INTO "topics_fts" VALUES('Духовне лідерство та морально-ціннісна стійкість у ЗС України',NULL);
CREATE INDEX idx_teachers_name 
                ON teachers(full_name)
            ;
CREATE INDEX idx_programs_name 
                ON educational_programs(name)
            ;
CREATE INDEX idx_topics_title 
                ON topics(title)
            ;
CREATE INDEX idx_disciplines_name
                ON disciplines(name)
            ;
CREATE INDEX idx_lessons_title 
                ON lessons(title)
            ;
CREATE INDEX idx_questions_content 
                ON questions(content)
            ;
CREATE TRIGGER teachers_ai AFTER INSERT ON teachers BEGIN
                INSERT INTO teachers_fts(rowid, full_name, position, department, email)
                VALUES (NEW.id, NEW.full_name, NEW.position, NEW.department, NEW.email);
            END;
CREATE TRIGGER teachers_ad AFTER DELETE ON teachers BEGIN
                DELETE FROM teachers_fts WHERE rowid = OLD.id;
            END;
CREATE TRIGGER teachers_au AFTER UPDATE ON teachers BEGIN
                UPDATE teachers_fts 
                SET full_name = NEW.full_name, position = NEW.position, 
                    department = NEW.department, email = NEW.email
                WHERE rowid = NEW.id;
            END;
CREATE TRIGGER programs_ai AFTER INSERT ON educational_programs BEGIN
                INSERT INTO programs_fts(rowid, name, description, level)
                VALUES (NEW.id, NEW.name, NEW.description, NEW.level);
            END;
CREATE TRIGGER programs_ad AFTER DELETE ON educational_programs BEGIN
                DELETE FROM programs_fts WHERE rowid = OLD.id;
            END;
CREATE TRIGGER programs_au AFTER UPDATE ON educational_programs BEGIN
                UPDATE programs_fts 
                SET name = NEW.name, description = NEW.description, level = NEW.level
                WHERE rowid = NEW.id;
            END;
CREATE TRIGGER topics_ai AFTER INSERT ON topics BEGIN
                INSERT INTO topics_fts(rowid, title, description)
                VALUES (NEW.id, NEW.title, NEW.description);
            END;
CREATE TRIGGER topics_ad AFTER DELETE ON topics BEGIN
                DELETE FROM topics_fts WHERE rowid = OLD.id;
            END;
CREATE TRIGGER topics_au AFTER UPDATE ON topics BEGIN
                UPDATE topics_fts 
                SET title = NEW.title, description = NEW.description
                WHERE rowid = NEW.id;
            END;
CREATE TRIGGER disciplines_ai AFTER INSERT ON disciplines BEGIN
                INSERT INTO disciplines_fts(rowid, name, description)
                VALUES (NEW.id, NEW.name, NEW.description);
            END;
CREATE TRIGGER disciplines_ad AFTER DELETE ON disciplines BEGIN
                DELETE FROM disciplines_fts WHERE rowid = OLD.id;
            END;
CREATE TRIGGER disciplines_au AFTER UPDATE ON disciplines BEGIN
                UPDATE disciplines_fts
                SET name = NEW.name, description = NEW.description
                WHERE rowid = NEW.id;
            END;
CREATE TRIGGER lessons_ai AFTER INSERT ON lessons BEGIN
                INSERT INTO lessons_fts(rowid, title, description)
                VALUES (NEW.id, NEW.title, NEW.description);
            END;
CREATE TRIGGER lessons_ad AFTER DELETE ON lessons BEGIN
                DELETE FROM lessons_fts WHERE rowid = OLD.id;
            END;
CREATE TRIGGER lessons_au AFTER UPDATE ON lessons BEGIN
                UPDATE lessons_fts 
                SET title = NEW.title, description = NEW.description
                WHERE rowid = NEW.id;
            END;
CREATE TRIGGER questions_ai AFTER INSERT ON questions BEGIN
                INSERT INTO questions_fts(rowid, content, answer)
                VALUES (NEW.id, NEW.content, NEW.answer);
            END;
CREATE TRIGGER questions_ad AFTER DELETE ON questions BEGIN
                DELETE FROM questions_fts WHERE rowid = OLD.id;
            END;
CREATE TRIGGER questions_au AFTER UPDATE ON questions BEGIN
                UPDATE questions_fts 
                SET content = NEW.content, answer = NEW.answer
                WHERE rowid = NEW.id;
            END;
CREATE INDEX idx_materials_title 
                ON methodical_materials(title)
            ;
CREATE TRIGGER materials_ai AFTER INSERT ON methodical_materials BEGIN
                INSERT INTO materials_fts(rowid, title, description, file_name)
                VALUES (NEW.id, NEW.title, NEW.description, NEW.file_name);
            END;
CREATE TRIGGER materials_ad AFTER DELETE ON methodical_materials BEGIN
                DELETE FROM materials_fts WHERE rowid = OLD.id;
            END;
CREATE TRIGGER materials_au AFTER UPDATE ON methodical_materials BEGIN
                UPDATE materials_fts 
                SET title = NEW.title, description = NEW.description, file_name = NEW.file_name
                WHERE rowid = NEW.id;
            END;
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('schema_migrations',9);
INSERT INTO "sqlite_sequence" VALUES('teachers',37);
INSERT INTO "sqlite_sequence" VALUES('educational_programs',25);
INSERT INTO "sqlite_sequence" VALUES('disciplines',30);
INSERT INTO "sqlite_sequence" VALUES('topics',68);
INSERT INTO "sqlite_sequence" VALUES('lessons',620);
INSERT INTO "sqlite_sequence" VALUES('questions',1684);
INSERT INTO "sqlite_sequence" VALUES('lesson_types',6);
INSERT INTO "sqlite_sequence" VALUES('material_types',8);
INSERT INTO "sqlite_sequence" VALUES('methodical_materials',113);
COMMIT;