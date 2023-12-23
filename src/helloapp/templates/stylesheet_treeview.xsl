<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" />

  <xsl:template match="/file">
    <ul id="file">
      <xsl:apply-templates />
    </ul>
  </xsl:template>

  <xsl:template match="*">
    <xsl:param name="path" select="''" />
    <xsl:variable name="currentPath" select="concat($path, '/', name())" />
    
    <xsl:choose>
    <xsl:when test="not(*)">
        <li>
          <xsl:value-of select="name()"/>: <input type="text" name="{$currentPath}" value="{.}"/> {% if el == '<xsl:value-of select="$currentPath" />' %}<span>{{ reason }}</span>{% endif %}
        </li>
    </xsl:when>
    <xsl:otherwise>
      <li>
          <span class="caret"><xsl:value-of select="name()"/></span>
          <ul class="nested">
            <xsl:apply-templates select="*">
              <xsl:with-param name="path" select="$currentPath" />
            </xsl:apply-templates>
          </ul>
      </li>
    </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>