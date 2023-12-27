# SoundBoard TG bot!
## Supported commands:
`/start`:
Adds user to the database. Responses "_Hi there! There is a list of my functions:
1) /add_sound <sound_name>. Use it in order to add a new sound into my storage. This sound will be available by this name later on. ➕
2) /list_sounds. Use it to view the list of sounds you added earlier that are currently available. 📌
3) /delete_sound <sound_name>. I suppose it's pretty clear what this command does 🧐
4) (inline) @myBotName <sound_name>. Use this command from any chat you want and choose your <sound_name>. I will send a voice message that contains your .mp3 file assosiated with this name. 🔊_"

`/list_sounds`:
Prints the list of sounds that were added by user and are currently available. Responses "Your sounds are:\n📌<sound_name_1>\n📌<sound_name_2> etc..."
If there are not any sounds, responds "_There are not any sounds in your collection! Feel free to add ones by using command /add_sound <sound_name>_"

`/add_sound <sound_name>`:
Waits for user to send a message with `.mp3` file attached. Adds this file to storage system and assosiates it with <sound_name>. This sound will be available by this name.
Following commands with the same <sound_name> will be ignored. If need to rewrite sound, use the `/delete_sound` command.

If there is no <sound_name>, responses "_Please tell me how to name a sound you want to attach! Tell me /add_sound <sound_name>_ ❌🤔" and does nothing else.

If there is already a file attached to <sound_name>, responses "_I already have a sound with that name! Please come up with something else!_ ❌😒"

If everything is OK, responses "Got it! Now please send a message with .mp3 file attached...".

###
Handling the next message:

If there is no file attached, responses "_Seems like there is no .mp3 file attached!_ ❌🧐" and does nothing else.

If there are more than one file attached, responses "_Seems like there are too many files!_ ❌🤓" and does nothing else.

If summary amount of disk space allocated for this user exceeds 100mb, responses "_Your disk space limit is reached! Try deleting some unused sounds first!_ ❌😢" and does nothing else.

If everything is OK, responses "_Good job! Your sound has been successfully added! Try sending it to somebody using @MyBoName inline command!_ ✅😎".

If there were no file since last execution of this command for this user and the current one is OK, responses "_Good job! Your sound has been successfully added! Previous attempts are forgotten!_ 🟨✅".

`/delete_sound <sound_name>`:

Deletes `.mp3` file assosiated with entered name from storage.

If there is no file assosiated with entered name, responses "_Didn't find a file assosiated with entered name "<sound_name>" in my storage!_ ❌😲" and does nothing else.

If everything is OK, responses "_This sound has been successfully deleted!_ ✅👾".

`@MyBotName <sound_name>` (inline bot's function):
Sends voice message containing a file assosiated with <sound_name>.
If there is no file assosiated with entered name, responses "_Didn't finda file assosiated with entered name "<sound_name>" in my storage!_ ❌😲" and does nothing else.


## .env:
```.env
BOT_NAME=

BOT_TOKEN=<bot api token>

DB_HOST=<host with postgresql>

DB_NAME=<database name>
 
DB_USER=<name database user>

DB_PASS=<password database user>
```
