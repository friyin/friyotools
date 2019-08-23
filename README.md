Friyo tools
===========

Your tools for fun and profit.



### Usage

#### Import domains into DB


Type `./domdata.py -i domains.txt` to import domains

If you specify dash - as input stdin will be used.

Example: `cat domains.txt | ./domdata.py -i -`

Result will be displayed to stdout showing new domains only.


#### List domains from DB

To list domains in DB: `./domdata.py -l`

At this moment not all details are dumped, you can use your favourite SQLite browser to see and modify stored data.


New versions
------------

This is an early preview, many features are coming. Stay tuned!

Happy hacking!
