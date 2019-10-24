# PRIESTESS
Self-disclosure chatbot for RocketChat and Discord

<h2>About</h2>

PRIESTESS is a Dutch chatbot written for an experiment at [Lowlands Science](https://lowlands.nl/programma/ll-science-geheimen-delen-met-een-chatbot/). It first tries to engage with a user by asking about their name and their experiences at Lowlands, after which the chatbot asks the user to confess a secret. 

The chatbot tries to reply to all information that the user provides with empathy (as much as a chatbot could do...). 

<h2>Installation</h2>

PRIESTESS is written in Python 3. For the chatbot you need the following libraries:

For both chatbot implementations:<br/>
[Regex](https://pypi.org/project/regex/)<br/>
[Pattern](https://www.clips.uantwerpen.be/pages/pattern/)<br/>
[Unidecode](https://pypi.org/project/Unidecode/)<br/>
[Pyspellchecker](https://pypi.org/project/pyspellchecker/)<br/>
[spaCy](https://spacy.io/usage/)<br/>
[xlrd](https://pypi.org/project/xlrd/)<br/>
[pytz](https://pypi.org/project/pytz/)<br/>

For the Discord version specifically:<br/>
[Discord.py](https://discordpy.readthedocs.io/en/latest/intro.html#installing/)

For the RocketChat version:<br/>
[Multiprocess](https://pypi.org/project/multiprocess/)<br/>
[RocketChat_API](https://github.com/jadolg/rocketchat_API/)

<h2>Usage</h2>

To activate PRIESTESS, you need to run <b>Discord_Interaction_Module.py</b> for the Discord implementation and 
<b>Governing_Module.py</b> for the RocketChat implementation.

<h3>But...</h3>

You need to set some things first: 

- PRIESTESS uses [LIWC](http://liwc.wpengine.com/). A commercial application. 
To use the LIWC integration, you need to purchase a license and put LIWC's dictionary file in the /Databases/ folder.

Then, set <b>line 447</b> in <b>Answer_Understanding_Module.py</b> to the LIWC filename.

- For Discord, set the ChatID and the Chatbot token in Datadict.json
- For Rocketchat, set ChatID, password, and username in Datadict.json and set the server_url in Governing_Module.py (line 424)

<h2>Modules</h2>

PRIESTESS is made with a modular structure to enable relatively easy modifications and additions.

- <b>Answer_Understanding_Module.py</b> contains all the natural language understanding functions to make sense of the chat answers. For this, the current version of PRIESTESS uses Pattern.nl's ([De Smedt, & Daelemans, 2012](http://www.jmlr.org/papers/volume13/desmedt12a/desmedt12a.pdf)) and LIWC 2015's ([Pennebaker et al., 2015](https://s3-us-west-2.amazonaws.com/downloads.liwc.net/LIWC2015_OperatorManual.pdf)) lexicon-based approaches.
- <b>Discord_Interaction_Module.py</b> or <b>Governing_Module.py</b> iterates over all the pre-set conversation topics, sends the messages linked to the topics, and activates the relevant modules after receiving an answer.
- <b>Lookup_Module.py</b> opens the template database and retrieves all the template categories and corresponding templates that are used by the chatbot
- <b>Participant_Number_Module.py</b> ensures that every user gets a new number assigned to them when saving the chats. Especially useful when you're doing experiments.
- <b>Template_Filler_Module.py</b> finds and fills the placeholder gaps in the templates. 
- <b>Template_Filler_Rule_Module.py</b> returns the relevant information to fill the gap in Template_Filler_Module.py.

Furthermore, RocketChat has some extra modules:

- <b>Chat_Interaction_Module.py</b> checks if a user has made a reply every n seconds. There's no fancy await/async integration for the RocketChat_API that I know of, so this was used as a workaround.
- <b>Extra_Commands_Module.py</b> contains some... extra commands. It's main use is to clear the chat after a participant has finished talking to PRIESTESS, to find the last message in the chat, and to find the first response to PRIESTESS's questions.
- <b>Save_Chat_Module.py</b> saves the chat. No surprises there.

Templates are Excel files found in the /Templates/ folder. They can easily be changed or translated to other languages. Databases are lexicons used by the spellchecker and by Answer_Understanding_Module.py to understand answers.

<h2>Contributions</h2>

- The Dutch spellcheck uses a lexicon derived from the SUBTIEL corpus ([Van der Lee & Van den Bosch, 2017](https://www.aclweb.org/anthology/W17-1224/))<br/>
- The Dutch first names database is based on first name data from [FROG](https://github.com/LanguageMachines/frog) ([Van den Bosch et al., 2007](https://ilk.uvt.nl/downloads/pub/papers/tadpole-final.pdf))<br/>
- Some of the models come from [PASS](https://github.com/tallchris91/pass) ([Van der Lee et al., 2017](https://www.aclweb.org/anthology/W17-3513))<br/>
