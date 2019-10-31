// create innodb cluster
var cluster = dba.createCluster('production', { adoptFromGR: true });


// query innodb cluster status
dba.getCluster('production').status();

