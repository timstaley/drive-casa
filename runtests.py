#!/usr/bin/env python

import sys
import pytest

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('iso8601').setLevel(logging.ERROR) #Suppress iso8601 debug log.
    pytest.main()
