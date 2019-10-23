# PRIESTESS
Self-disclosure chatbot for RocketChat and Discord

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
[RocketChat_API](https://github.com/jadolg/rocketchat_API/)

For the Discord version specifically:
[Discord.py](https://discordpy.readthedocs.io/en/latest/intro.html#installing/)

For the RocketChat version:
[Multiprocess](https://pypi.org/project/multiprocess/)

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

<h2>Contributions</h2>
- The Dutch spellcheck was made possible thanks to the SUBTIEL corpus (Van der Lee & Van den Bosch, 2017)
- The Dutch first names database is based on the first name data from FROG (Van den Bosch et al., 2007)
- The modular structure is based on PASS (Van der Lee et al., 2017)
