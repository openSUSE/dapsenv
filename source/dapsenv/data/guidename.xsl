<?xml version="1.0" encoding="UTF-8"?>
<!-- 
  Purpose:
    Returns title of book or article

  Parameters:
    * rootid
      Applies stylesheet only to part of the document

  Author(s):  Thomas Schraitle <toms@opensuse.org>

  Copyright:  2016 Thomas Schraitle

-->
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:d="http://docbook.org/ns/docbook">

 <xsl:import href="rootid.xsl"/>
 <xsl:output method="text"/>

 <xsl:template match="text()"/>

 <xsl:template match="d:set/d:title | d:set/d:info/d:title |
                      d:book/d:title | d:book/d:info/d:title |
                      d:article/d:title | d:article/d:info/d:title">
  <xsl:value-of select="string(.)"/>
 </xsl:template>

 <xsl:template match="set/title | set/setinfo/title |
                      book/title | book/bookinfo/title |
                      article/title | article/articleinfo/title">
   <xsl:value-of select="string(.)"/>
 </xsl:template>

</xsl:stylesheet>
