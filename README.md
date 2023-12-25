# SoundBoard TG bot!
## Supported commands:
`@start`:
Adds user to the database.

`@add_sound <sound_name>`:
Waits for user to send a message with `.mp3` file attached. Adds this file to storage system and assosiates it with <sound_name>. This sound will be available by this name.
Following commands with the same <sound_name> will be ignored. If need to rewrite sound, use the `@delete_sound` command.

If there is no file attached, responses _Seems like there is no .mp3 file attached! 🧐`_ and does nothing else.

If there are more than one file attached, responses _Seems like there are too many files! 🤓_ and does nothing else.

`@delete_sound <sound_name>`:

Deletes `.mp3` file assosiated with entered name from storage.

If there is no file assosiated with entered name, responses _Didn't find file assosiated with entered <sound_name> in my storage! 😲_ and does nothing else.

`@play <sound_name>`:
Sends voice message containing file assosiated with <sound_name>.
If there is no file assosiated with entered name, responses _Didn't find file assosiated with entered <sound_name> in my storage! 😲_ and does nothing else.

