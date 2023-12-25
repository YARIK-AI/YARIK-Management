<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" />

  <xsl:template match="/xml_repr">
    <table>
      <tr border="1" bgcolor="#9acd32">
        <th>Параметр</th>
        <th>Значение</th>
      </tr>
      <xsl:apply-templates/>
    </table>
  </xsl:template>

  <xsl:template match="*">
    <xsl:param name="path" select="''" />
    <xsl:variable name="currentPath" select="concat($path, '/', name())" />
    
    <xsl:choose>
      <xsl:when test="not(*)">
        <tr>
          <td><xsl:value-of select="$currentPath"/></td>
          <td><input type="text" name="{$currentPath}" value="{.}"/></td>
          {% if el == '<xsl:value-of select="$currentPath" />' %}<td><span>{{ reason }}</span></td>{% endif %}
        </tr>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="not(@*)">
            <xsl:apply-templates select="*">
              <xsl:with-param name="path" select="$currentPath" />
            </xsl:apply-templates>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="*">
              <xsl:with-param name="path" select="concat($currentPath, '[@n=&quot;', @n, '&quot;]')" />
            </xsl:apply-templates>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


</xsl:stylesheet>