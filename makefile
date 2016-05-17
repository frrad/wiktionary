all: enwiktionary-latest-pages-articles.xml.bz2 python-libraries

enwiktionary-latest-pages-articles.xml.bz2:
	curl https://dumps.wikimedia.org/enwiktionary/latest/enwiktionary-latest-pages-articles.xml.bz2 -o enwiktionary-latest-pages-articles.xml.bz2

python-libraries:
	pip install -r requirements.txt && touch python-libraries

clean:
	rm python-libraries
