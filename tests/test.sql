INSERT INTO
  books (isbn, title, total)
VALUES
  ('978-7-12115-535-2', 'C++ Primer', 5);
INSERT INTO
  books (isbn, title, total)
VALUES
  (
    '978-0-87779-906-1',
    'The Merriam-Webster Dictionary of Synonyms and Antonyms',
    2
  );
INSERT INTO
  entries (user_id, type, book_id, detail)
VALUES
  ('root', 'N', 1, 'Amount: 5');
INSERT INTO
  entries (user_id, type, book_id, detail)
VALUES
  ('root', 'N', 2, 'Amount: 2');