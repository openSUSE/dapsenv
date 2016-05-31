<?xml version="1.0" encoding="UTF-8"?>
<!-- 
  Purpose:
    Returns productnumber of the guide

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

 <xsl:template match="d:set/d:info/d:productnumber[1] |
                      d:book/d:info/d:productnumber[1] |
                      d:article/d:info/d:productnumber[1]">
  <xsl:value-of select="string(.)"/>
 </xsl:template>

 <xsl:template match="set/setinfo/productnumber[1] |
                      book/bookinfo/productnumber[1] |
                      article/articleinfo/productnumber[1]">
  <xsl:value-of select="string(.)"/>
 </xsl:template>


</xsl:stylesheet>
