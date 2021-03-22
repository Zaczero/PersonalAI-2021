# PersonalAI 2021

```txt
D.I.Y.
Unethical AI
If you insult it,
It is gonna make you cry.
```

This is a school project using which everyone will be able to create their very own personal AI. All it requires is a few hundred lines of Q&A training data and a Microsoft Azure account *(used for TTS\* and STT)*. Generated answers are not in any way creative as the AI is based on comparing sentence similarities and reading out matched question's answer. This project has a Speech-to-Text integration using which you will be able to hook up the AI to almost any online meeting software for people to converse with.

\*It is also possible to pre-record your own TTS answers using a custom voice.

## Check out this demo

[![asciicast](https://asciinema.org/a/wCDLofeKgSnHrN8LQ3AQo8z5A.svg)](https://asciinema.org/a/wCDLofeKgSnHrN8LQ3AQo8z5A)

## File structure

* `/AnswerGeneration` - Project responsible for generating answers to given questions.
* `/data` - Primary data store directory *(QA file, audio recordings and cache)*.
* `/Engine` - Main project which wraps everything together.
* `/misc` - Miscalenous files used during the school presentation.
* `/VoiceRecorder` - Project used for quick recording of voice samples.

## Getting started

1. Prepare your Microsoft Azure account with Cognitive Services installed *(available for free for limited use)*.
2. Create `/Engine/.env` file and define your `AZURE_KEY` and `AZURE_REGION` environment variables there. Values of both of those variables are dependant on your Cognitive Services installation.
3. Inside the `get_wav_path(...)` function in the `Engine` project update the audio cache directory path. Ensure that the directory has write permissions. Whenever there is no corresponding audio file found, an Azure TTS will be generated. To use a custom voice instead, simply populate the cache with `VoiceRecorder` recording files.
4. Done, you are now ready to run the project - have fun.

## Things that are not right

* Import of the `AnswerGenration` module inside the `Engine` project requires some trickery with `PATH` environment variable. Simple project restructure will solve that problem, however, I did not bother with fixing that.

* Generating an Azure TTS may sometimes fail whenever doing a coldstart *(timeout issue)*. Processing the same sentence for the second time will most likely generate a proper TTS audio file.

* The `Engine` project is using system's default audio in/out devices. That's not an ideal solution as you have to manually route your audio using virtual cables. I had some problem with getting custom devices to work on the Azure side as it requires you to provide devices in system-dependent device endpoint format. The other solution is to use `PullAudioInputStreamCallback` but I could not get it to work. I just did not want to spend any more time on fixing that, sorry.

## Footer

### 📧 Contact

* Email: [kamil@monicz.pl](mailto:kamil@monicz.pl)
* PGP: [0x9D7BC5B97BB0A707](https://gist.github.com/Zaczero/158da01bfd5b6d236f2b8ceb62dd9698)

### 📃 License

* [Zaczero/PersonalAI-2021](https://github.com/Zaczero/PersonalAI-2021/blob/main/LICENSE)
