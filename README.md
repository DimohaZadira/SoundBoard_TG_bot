# SoundBoard TG bot!
## Supported commands:
`/start`:
Adds user to the database.

`/add_sound <sound_name>`:
Waits for user to send a message with `.mp3` file attached. Adds this file to storage system and assosiates it with <sound_name>. This sound will be available by this name.
Following commands with the same <sound_name> will be ignored. If need to rewrite sound, use the `@delete_sound` command.

If there is no file attached, responses "_Seems like there is no .mp3 file attached!_ ❌🧐" and does nothing else.

If there are more than one file attached, responses "_Seems like there are too many files!_ ❌🤓" and does nothing else.

If summary amount of disk space allocated for this user exceeds 100mb, responses "_Your disk space limit is reached! Try deleting some unused sounds first!_ ❌😢" and does nothing else.

If everything is OK, responses "_Good job! Your sound has been successfully added! Try sending it to somebody using @play command!_ ✅😎".

If there were no file since last execution of this command for this user and the current one is OK, responses "_Good job! Your sound has been successfully added! Previous attempts are forgotten!_ 🟨✅".

`/delete_sound <sound_name>`:

Deletes `.mp3` file assosiated with entered name from storage.

If there is no file assosiated with entered name, responses "_Didn't find file assosiated with entered <sound_name> in my storage!_ ❌😲" and does nothing else.

If everything is OK, responses "_This sound has been successfully deleted!_ ✅👾".

`/play <sound_name>`:
Sends voice message containing file assosiated with <sound_name>.
If there is no file assosiated with entered name, responses "_Didn't find file assosiated with entered <sound_name> in my storage!_ ❌😲" and does nothing else.

