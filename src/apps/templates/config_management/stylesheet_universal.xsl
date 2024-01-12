<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" />

  <xsl:template match="/xml_repr">
  {% load filters %}
    <table id="tbl" rules="rows">
      <thead>
      <tr class="table-head">
        <th>Name</th>
        <th>Description</th>
        <th>Value</th>
      </tr>
      </thead>
      <tbody >
      <xsl:apply-templates/>
      </tbody>
    </table>
    <div id="pagination" class="pages"></div>
  </xsl:template>

  <xsl:template match="*">
    <xsl:param name="path" select="''" />
    <xsl:variable name="currentPath" select="concat($path, '/', name())" />
    
    <xsl:choose>
      <xsl:when test="not(*)">
        <tr>
          <td class="c1">{{ params|get_name_by_key:&apos;<xsl:value-of select="$currentPath"/>&apos; }}</td>
          <td class="c2">{{ params|get_desc_by_key:&apos;<xsl:value-of select="$currentPath"/>&apos; }}</td>
          <td class="c3">
          {% if el == '<xsl:value-of select="$currentPath" />' %}
            <xsl:choose>
                <xsl:when test="@type = 'checkbox'">
                  <xsl:if test=". = 'true'">
                    <input class="err_in" type="{@type}" name="{$currentPath}" value="true" checked="1" />
                  </xsl:if>
                  <xsl:if test=". = 'false'">
                    <input class="err_in" type="{@type}" name="{$currentPath}" value="true"/>
                  </xsl:if>
                </xsl:when>
                <xsl:otherwise>
                  <input class="err_in" type="{@type}" name="{$currentPath}" value="{.}" />
                </xsl:otherwise>
              </xsl:choose>
            <span>{{ reason }}</span>
          {% else %}
              <xsl:choose>
                <xsl:when test="@type = 'checkbox'">
                  <xsl:if test=". = 'true'">
                    <input type="{@type}" name="{$currentPath}" value="true" checked="1" />
                  </xsl:if>
                  <xsl:if test=". = 'false'">
                    <input type="{@type}" name="{$currentPath}" value="true" />
                  </xsl:if>
                </xsl:when>
                <xsl:otherwise>
                  <input type="{@type}" name="{$currentPath}" value="{.}" />
                </xsl:otherwise>
              </xsl:choose>
          {% endif %}
          </td>
          
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