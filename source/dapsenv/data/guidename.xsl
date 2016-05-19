<!-- 
  Purpose:
    Returns title of book or article

  Author(s):  Thomas Schraitle <toms@opensuse.org>

  Copyright:  2016 Thomas Schraitle

-->
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:d="http://docbook.org/ns/docbook">

 <xsl:output method="text"/>

 <xsl:template match="text()"/>


 <!-- ================================================================= -->
 <!-- DocBook 5 -->

 <xsl:template match="d:article/d:title | d:article/d:info/d:title">
  <xsl:value-of select="text()"/>
  <xsl:apply-templates/>
 </xsl:template>

 <xsl:template match="d:book/d:title | d:book/d:info/d:title">
  <xsl:value-of select="text()"/>
  <xsl:apply-templates/>
 </xsl:template>

 <xsl:template match="d:book/d:title/* | d:book/d:info/d:title/*">
  <xsl:value-of select="text()"/>
 </xsl:template>

 <!-- ================================================================= -->
 <!-- DocBook 4 -->

 <xsl:template match="article/title | article/articleinfo/title">
  <xsl:value-of select="text()"/>
  <xsl:apply-templates/>
 </xsl:template>

 <xsl:template match="book/title | book/bookinfo/title">
  <xsl:value-of select="text()"/>
  <xsl:apply-templates/>
 </xsl:template>

 <xsl:template match="book/title/* | book/bookinfo/title/*">
  <xsl:value-of select="text()"/>
 </xsl:template>

</xsl:stylesheet>
