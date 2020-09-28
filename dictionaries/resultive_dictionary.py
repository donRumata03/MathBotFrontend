#
# import sys
# sys.path.insert(0, '../')
#

import config

from dictionaries.common_dictionary import *

if config.intelligent_mode_on:
    from dictionaries.intelligent_dictionary import *
else:
    from dictionaries.brute_dictionary import *
