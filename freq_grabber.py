#!/usr/bin/python

import sys
import ConfigParser
import query_engines
from query_engines import WSError

# Constants
CONFIG_FILE = 'configuration.ini'
QUERY_ENGINE_DICT = {
        "SCN":query_engines.SCN,
        "BNC":query_engines.BNC
    }

# Main
def main():

    query_engine_list = list() # [[engine_name, output_file, engine_instance],..]

    try:
        # read configuration
        (word_file_ptr, debug,
         query_engine_dict, query_engine_names) = load_config_file(CONFIG_FILE)

        # load and init query engines
        for engine_name in query_engine_names:
            username     = query_engine_dict[engine_name].get("username")
            password     = query_engine_dict[engine_name].get("password")
            output_file  = query_engine_dict[engine_name].get("output_file")

            engine_obj = QUERY_ENGINE_DICT.get(engine_name)
            engine_instance = engine_obj(username, password, debug)
            init_csv(output_file)
            query_engine_list.append([engine_name, output_file, engine_instance])

    except WSError, err:
        print "Error: %s" % str(err)
        sys.exit(1)

    try:
        # run queries, word by word
        lines = word_file_ptr.readlines()
        count = len(lines)
        for index, line in enumerate(lines):
            word = line.strip()

            print ("Getting data.. %d/%d (%d%%)" %
                   (index+1, count, (index+1)*100/count))

            # query all engines
            for engine_name, output_file, engine_instance in query_engine_list:
                if debug:
                    print "Querying %s.." % engine_name
                result = engine_instance.query(word)
                append_result(output_file, result)

        print "Done. saved to:"
        for engine_name, output_file, engine_instance in query_engine_list:
            print output_file

    except WSError, err:
        print "Error: %s" % str(err)
        if debug:
            print "=== DEBUG Info ===\n%s\n==================" % err.get_debug_info()

# Functions
def load_config_file(file_name):
    """
    Parse configuration file, load word file, and return query_engine_dict.
    Returns: (word_file_ptr, debug, query_engine_dict)
    query_engine_dict = {query_engine:{field:value}}
    Exceptions: WSError
    """
    query_engine_dict = dict()

    config = ConfigParser.ConfigParser()
    file_list = config.read(file_name)
    if not file_name in file_list:
        print file_list
        raise WSError("Couldn't open configuration file: %s" % file_name)

    # get general configuration
    if "General" in config.sections():
        # get word file
        if config.has_option("General", "word_list_file"):
            word_file = config.get("General", "word_list_file")
        else:
            raise WSError("Couldn't find 'word_list_file' parameter in" +
                          " 'General' section in the configuration file")

        # get debug_mode
        if config.has_option("General", "debug"):
            if config.get("General", "debug") != '0':
                debug = True
            else:
                debug = False
        else:
            raise WSError("Couldn't find 'debug' parameter in" +
                          " 'General' section in the configuration file")

        # get query_engines
        if config.has_option("General", "query_engines"):
            query_engines_str = config.get("General", "query_engines")

            # convert to a list
            query_engine_list = map(lambda x: x.strip(),
                                     query_engines_str.split(','))

            # validate list
            for query_engine in query_engine_list:

                # check that we have this kind of engine
                if query_engine not in QUERY_ENGINE_DICT:
                    raise WSError("Unknown query engine: %s" % query_engine)

                # check that we have configuration for that engine
                if query_engine not in config.sections():
                    msg = ("Can't find configuration for '%s' query engine" %
                           query_engine)
                    raise WSError(msg)
        else:
            raise WSError("Couldn't find 'query_engines' parameter in" +
                          " 'General' section in the configuration file")
    else:
        raise WSError("Couldn't find 'General' section in the configuration file")

    # open word_file
    word_file_ptr = None
    try:
        word_file_ptr = open(word_file, 'r')
    except Exception, err:
        raise WSError("Couldn't open word_file: %s. err: %s" %
                      (word_file, str(err)))

    # iterate over sections in conf file
    for section in config.sections():
        if section != "General":
            query_engine_dict[section] = dict(config.items(section))

            # validate query_engine has required fields
            for field in ['username', 'password', 'output_file']:
                if field not in query_engine_dict[section]:
                    raise WSError("Couldn't find '%s' field for '%s' in %s" %
                                  (field, section, file_name))

    return word_file_ptr, debug, query_engine_dict, query_engine_list

def init_csv(csv_file_name):
    """
    Initialize csv output file.
    Exceptions: WSError
    """

    csv_file_ptr = None
    try:
        csv_file_ptr = open(csv_file_name, 'w')
    except Exception, err:
        raise WSError("Couldn't write to output file: %s" % csv_file_name)

    csv_file_ptr.write("word,hit_count,per_million\n")
    csv_file_ptr.close()

def append_result(csv_file_name, result):
    """
    Append result to csv file
    result = (word, hit_count, per_million)
    Exceptions: WSError
    """

    csv_file_ptr = None
    try:
        csv_file_ptr = open(csv_file_name, 'a')
    except Exception, err:
        raise WSError("Couldn't write to output file: %s" % csv_file_name)

    csv_file_ptr.write(','.join(result) + '\n')
    csv_file_ptr.close()

# Classes

# Main
if __name__ == "__main__":
    main()