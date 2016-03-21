# Reindexing jenkins data

`logstash-reindex-jenkins.conf` is logstash configuration for the reindexing of `rhci-logstash-YYYY.MM.DD` indicies to the new `rhci-logs-YYYY.MM.DD` indices (based on the mapping of the parent directory).

The config corresponds to reindexing from the initial version to template version *2016.03.21.0*

## Running

1. Copy [patterns/date](patterns/date) to `/opt/logstash/patterns` or edit the logstash configuration file.
2. Edit Logstash config to specify proper input and output ElasticSearch servers
3. Edit Logstash config to specify the indices you want to reindex
4. Run(assuming Logstash is installed in /opt/logstash/):  

> /opt/logstash/bin/logstash -f logstash-reindex-jenkins.conf

The file is created manually.

Tests - TBD...
