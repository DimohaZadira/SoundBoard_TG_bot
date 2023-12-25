# SoundBoard TG bot!
## Supported commands:
`@start`:
Adds user to the database.
`@add_sound <sound_name>`:
Waits for you to send a message with `.mp3` file attached. Adds this file to storage system and assosiates it with <sound_name>. This sound will be available by this name.
Following commands with the same <sound_name> will be ignored. If need to rewrite sound, use the following command.
`@delete_sound <sound_name>`:
Deletes `.mp3` file assosiated with entered name from storage.
`@play <sound_name>`:
Sends voice message containing file assosiated with <sound_name>.

