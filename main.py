"""
Webservice that acts as the glue between Amazon and MongoDB.
"""

NYTIMES_API_KEY = None

def initialize():
    global NYTIMES_API_KEY
    if not NYTIMES_API_KEY:
        with open('nytimes-key') as nytimes:
            NYTIMES_API_KEY = nytimes.read()

def main():
    initialize()


if __name__ == '__main__':
    main()

