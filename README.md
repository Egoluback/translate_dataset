# translate_dataset
Python-script that translates your dataset into one of general languages using DeepL translator(parsing). <br />
Script uses selenium web-scrapping tool to load and parse data from translator site. <br />
It has dynamic logging system: progress updates every line, and every 50 lines backup happens. It also can load from save point if parsing process was interrupted. In cause of error webdriver reboots and this line is being skipped. <br />
The result will be located in "-trans" column(s). 
