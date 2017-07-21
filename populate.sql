INSERT INTO User (username, password)
VALUES ("admin", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"),
		("not_admin", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918");

INSERT INTO Board (userId, name, lastModified)
VALUES (1, 'First Board', datetime('now','-2 hours')),
	   (1, 'Anotha one', datetime('now','-20 hours')),
	   (1, "Admin's third", datetime('now', '-1 minute')),
	   (1, 'ickabickaboo', datetime('now','-1 day')),
	   (1, '#Blessed', datetime('now','-20 minutes')),
	   (2, "Not admin's board", datetime('now'));