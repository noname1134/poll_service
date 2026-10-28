CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title TEXT NOT NULL,
    option_1 TEXT NOT NULL,
	option_2 TEXT NOT NULL,
	option_3 TEXT NOT NULL,
	option_4 TEXT NOT NULL
);

CREATE TABLE answers (
    user_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_option INT NOT NULL,
	PRIMARY KEY (user_id, question_id),
	CHECK (selected_option BETWEEN 1 AND 4),
	FOREIGN KEY (question_id) REFERENCES questions(id)
	    ON DELETE CASCADE
);
