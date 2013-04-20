FreqGrabber
===========

About
-----
This script queries the web interfaces of two corpora for statistics about word usage in the English language.
The script reads a list of words from a file, and creates CSV files that contain:

- the absolute amount of occurrences of the word in the corpus, and 
- the relative frequency of each word per million words in the corpus.

The corpora queried are:

- The British National Corpus (BNC) - A corpus designed to represent British English as a whole, as it was used between the years 1960-1993. It was designed to represent as wide a range of the language as possible, with both a written part (90%) and a spoken part (10%). It contains 100,106,008 words, and it was compiled by the BNC Consortium, an industrial/academic consortium led by Oxford University Press. 
- The Professional English Research Consortium Corpus (PERC) - Formerly called the "Corpus of Professional English" or CPE. This is a 17-million-word corpus of English academic journal texts from the journals with the top 20% impact factor within 22 fields in science, engineering, technology and other fields.  It was compiled by The Professional English Research Consortium (PERC), a Japan-based association of scholars, educators, publishers, test developers, etc.

Requirements
------------
- Python. [Download here](http://www.python.org/download) (Please download version 2.7.* and not 3.*)

Files
-----
- LICENSE: License documentation.
- run_windows.bat & run_linux.sh: Run the script.
- freq_grabber.py: Main script.
- query_engines.py: Implements query engines (engine per web-site)
- configuration.ini: Main configuration file.
- words.txt: Default word list (can be changed in configuration.ini)

Usage
-----
- Set your preferences in the configuration file ("configuration.ini"),
- Add words you want to query to the word_list_file (look at the configuration file) one word per line.
- Run the script (run_windows.bat or run_linux.sh).
- Use the generated CSV files.

Configuration.ini
-----------------
The configuration file was composed for two parts: general configuration, and engine configuration.

General configuration:

- word_list_file: The name of the file that contains the word list.
- query_engines: A list of query engines that will give statistics about each word in the word list.
- debug: if equals 1, include debugging messages and more verbose error messages.
 
Engine configuration:
Every engine has its own parameters.

- username: login user name to the site.
- password: login password to the site.
- output_file: Name of the CSV file with the statistical information about the word list.
