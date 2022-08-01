-- SELECT id, type, value FROM tags WHERE __ts_vector__ @@ phraseto_tsquery('english', 'MSBuild.exe');
-- SELECT id, type, value FROM tags WHERE VALUE LIKE '%MSBuild.exe%';
SELECT * FROM tags JOIN artifacts_tags ON tags.id=artifacts_tags.tag_id WHERE artifact_id = 1;