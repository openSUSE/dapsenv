#
# this make file builds the dapsenv man page
#

DB := http://docbook.sourceforge.net/release/xsl/current/
BUILDDIR := build
XMLFILE := dapsenv.xml
OUTFILE := dapsenv.1

.PHONY: all clean

all: clean $(BUILDDIR)
	xmllint --noout --xinclude --postvalid xml/$(XMLFILE)
	xsltproc --xinclude --nonet $(DB)/manpages/docbook.xsl xml/$(XMLFILE)
	mv $(OUTFILE) $(BUILDDIR)

clean:
	-rm -rf $(BUILDDIR)

$(BUILDDIR):
	mkdir $(BUILDDIR)
