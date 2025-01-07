# Use base image
FROM solr:9.7

# Create the default configset folder
RUN mkdir -p /opt/solr/server/solr/configsets/_default/conf

# Copy the schema.xml and solrconfig.xml to the default configset
# COPY schema.xml /opt/solr/server/solr/configsets/_default/conf/
# COPY solrconfig.xml /opt/solr/server/solr/configsets/_default/conf/

# Set permissions
USER root
RUN chown -R solr:solr /opt/solr/server/solr/configsets
USER solr

# Create a core with the custom configset
CMD ["solr-precreate", "fbs", "/opt/solr/server/solr/configsets/_default"]
