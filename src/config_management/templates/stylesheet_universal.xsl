<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" />

  <xsl:template match="/xml_repr">
  {% load filters %}
    <table>
      <tr class="table-head">
        <th>Name</th>
        <th>Description</th>
        <th>Value</th>
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
          <td id="1">{{ params|get_name_by_key:&apos;<xsl:value-of select="$currentPath"/>&apos; }}</td>
          <td id="2">{{ params|get_desc_by_key:&apos;<xsl:value-of select="$currentPath"/>&apos; }}</td>
          <td id="3"><input type="text" name="{$currentPath}" value="{.}"/></td>
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