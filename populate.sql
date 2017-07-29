INSERT INTO User (username, password)
VALUES ("admin", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"),
		("not_admin", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918");

INSERT INTO Board (userId, name, lastModified, isPublic)
VALUES (1, 'First Board', datetime('now','-2 hours'), true),
	   (1, 'Anotha one', datetime('now','-20 hours'), true),
	   (1, "Admin's third", datetime('now', '-1 minute'), false),
	   (1, 'ickabickaboo', datetime('now','-1 day'), true),
	   (1, '#Blessed', datetime('now','-20 minutes'), false),
	   (2, "Not admin's board", datetime('now'), false);