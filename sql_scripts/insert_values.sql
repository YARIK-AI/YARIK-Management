INSERT INTO artifacts.modules (id,"name",description) VALUES
	 (1,'Visualization','Module containing services for data visualization'),
	 (2,'Storage','Data storage module'),
	 (3,'Administration','Administration module'),
	 (4,'ETL','Data processing module');


INSERT INTO artifacts.components (id,"name",description,module_id) VALUES
	 (1,'PostgreSQL','The artifact storage component is a PostgreSQL database. Designed to store parameters of configuration files of YARIK platform components.',2),
	 (2,'Superset','Open source BI platform',1),
	 (3,'Grafana','Open source IT monitoring system',1),
	 (4,'Clickhouse','Column oriented-analytical open source DBMS',2),
	 (5,'Airflow','Open source workflow namagement platform for data engeneering pipelines',4),
	 (6,'NiFi','Open source data flow automatization software',4),
	 (7,'Component1','Description',4),
	 (8,'Component2','Description',4),
	 (9,'Component3','Description',4),
	 (10,'Component4','Description',2),
	 (11,'Component5','Description',2),
	 (12,'Component6','Description',2),
	 (13,'Component7','Description',1),
	 (14,'Component8','Description',1),
	 (15,'Component9','Description',1),
	 (16,'Component10','Description',3),
	 (17,'Component11','Description',3),
	 (18,'Component12','Description',3),
	 (19,'Component13','Description',4),
	 (20,'Component14','Description',1);


INSERT INTO artifacts.applications (id,"name",description,component_id) VALUES
	 (1,'Superset app','Application - Superset - main application in component.',2),
	 (2,'Redis','Application - Redis - cache storage for superset',2),
	 (3,'PostgreSQL','Application - PostgreSQL - database for storage superset objects',2),
	 (4,'PostgreSQL','Application - PostgreSQL - database for storage configuration parameters',1),
	 (5,'Clickhouse','Application - Clickhouse - DBMS',4),
	 (6,'Clickkeeper','Application - Clickkeeper - coordination service like zookeeper, but for clickhouse',4),
	 (7,'Ubuntu','OS OS OS',7);



INSERT INTO artifacts.instances (id,"name","version",description,app_id) VALUES
	 (1,'Clickhouse01','23.11.2.11','First instance of Clickhouse app',5),
	 (2,'Clickhouse02','23.11.2.11','Second instance of Clickhouse app',5),
	 (3,'Clickkeeper01','23.3','First instance of Clickkeeper app',6),
	 (4,'Clickkeeper02','23.3','Second instance of Clickkeeper app',6),
	 (5,'Superset01','2.1.1','First instance of Superset app',1),
	 (6,'RedisSuperset01','7.2.3','First instance of Redis for Superset app',2),
	 (7,'PostgreSQLSuperset01','16.1','First instance of PostgreSQL for Superset app',3),
	 (8,'PostgreSQL01','16.1','First instance of PostgreSQL app',4),
	 (9,'Ubuntu01','24.04','OS UBUNTU INSTANCE',7);



INSERT INTO artifacts.files (id,"name",description,filename,ftype,fencoding,path_prefix,gitslug_postfix,xslt_gitslug_postfix,xsd_gitslug_postfix,instance_id) VALUES
	 (1,'PostgreSQL01 Deployment manifest','Manifest for deploying PostgreSQL01 in k8s','postgres.yaml','yaml','utf-8','postgres/postgres/postgres01/','file/postgres.yaml','xslt/postgres.xml','xsd/postgres.xsd',true,8),
	 (2,'PostgreSQL01 service manifest','Manifest for providing PostgreSQL01 service in k8s','service.yaml','yaml','utf-8','postgres/postgres/postgres01/','file/service.yaml','xslt/service.xml','xsd/service.xsd',true,8),
	 (3,'Superset01 Deployment manifest','Manifest for deploying Superset01 in k8s','superset.yaml','yaml','utf-8','superset/superset/superset01/','file/superset.yaml','xslt/superset.xml','xsd/superset.xsd',true,5),
	 (4,'RedisSuperset01 Deployment manifest','Manifest for deploying RedisSuperset01 in k8s','redis.yaml','yaml','utf-8','superset/redis/redis01/','file/redis.yaml','xslt/redis.xml','xsd/redis.xsd',true,6),
	 (5,'PostgreSQLSuperset01 Deployment manifest','Manifest for deploying PostgreSQLSuperset01 in k8s','postgres.yaml','yaml','utf-8','superset/postgres/postgres01/','file/postgres.yaml','xslt/postgres.xml','xsd/postgres.xsd',true,7),
	 (6,'Ubuntu01 deployment manifest','Manifest for deploying Ubuntu01 in k8s','ubuntu.yaml','yaml','ubuntu/ubuntu/','Component1/ubuntu/ubuntu01/','file/ubuntu.yaml','xslt/ubuntu.xml','xsd/ubuntu.xsd',true,9);
	 
	
INSERT INTO artifacts.parameters (id,"name",description,absxpath,value,input_type,file_id,default_value) VALUES
	 (8,'Name of 1 volume','This must match the Name of a Volume.','/ubuntu/spec/template/spec/containers/volumeMounts[@n="1"]/name','ubuntu-data','ubuntu-data','text',6),
	 (12,'Readonly flag for 2 volume mount','Mounted read-only if true, read-write otherwise.','/ubuntu/spec/template/spec/containers/volumeMounts[@n="2"]/readOnly','false','false','checkbox',6),
	 (10,'Mount path for 2 volume','Path within the container at which the volume should be mounted. Must not contain ":".','/ubuntu/spec/template/spec/containers/volumeMounts[@n="2"]/mountPath','/home/sdl/weg','/home/sdl/weg','text',6),
	 (11,'Name of 2 volume','This must match the Name of a Volume.','/ubuntu/spec/template/spec/containers/volumeMounts[@n="2"]/name','ubuntu-weg','ubuntu-weg','text',6),
	 (16,'Custom','Custom parameters in json format.','/postgres/custom','{"m": "10", "y": "4"}','{"m": "10", "y": "4"}','textarea',1),
	 (4,'Required cpu','Describes the minimum amount of cpu required','/ubuntu/spec/template/spec/containers/resources/requests/cpu','3','3','number',6),
	 (1,'Container port','Number of port to expose on the pods IP address. This must be a valid port number, 0 < x < 65536.','/postgres/spec/template/spec/containers/ports/containerPort','5432','5432','number',1),
	 (2,'Number of replicas','This is the number of desired replicas. This is a pointer to distinguish between explicit zero and unspecified','/postgres/spec/replicas','1','1','number',1),
	 (17,'Init container image name','Image name in repository/name:version format','/superset/spec/template/spec/initContainers/image','aggrik/superset:2.1.0','aggrik/superset:2.1.0','text',3),
	 (18,'Container image name','Image name in repository/name:version format','/superset/spec/template/spec/containers/image','aggrik/superset:2.1.0','aggrik/superset:2.1.0','text',3),
	 (19,'Container image name','Image name in repository/name:version format','/redis/spec/template/spec/containers/image','aggrik/redis:latest','aggrik/redis:latest','text',4),
	 (20,'Init container image name','Image name in repository/name:version format','/postgres/spec/template/spec/initContainers/image','aggrik/postgresql:latest','aggrik/postgresql:latest','text',5),
	 (21,'Container image name','Image name in repository/name:version format','/postgres/spec/template/spec/containers/image','aggrik/postgresql:latest','aggrik/postgresql:latest','text',5),
	 (14,'Node port','The port on each node on which this service is exposed when type is NodePort or LoadBalancer.','/postgres/spec/ports/nodePort','32321','32321','number',2),
	 (15,'Port','The port that will be exposed by this service.','/postgres/spec/ports/port','3239','3239','number',2),
	 (3,'Required memory','Describes the minimum amount of ram required','/ubuntu/spec/template/spec/containers/resources/requests/memory','2Gi','2Gi','text',6),
	 (5,'Max memory','Describes the maximum amount of ram resources allowed','/ubuntu/spec/template/spec/containers/resources/limits/memory','2Gi','2Gi','text',6),
	 (13,'Target port','Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME.','/postgres/spec/ports/targetPort','5433','5433','number',2),
	 (9,'Readonly flag for 1 volume mount','Mounted read-only if true, read-write otherwise.','/ubuntu/spec/template/spec/containers/volumeMounts[@n="1"]/readOnly','false','false','checkbox',6),
	 (6,'Max cpu','Describes the maximum amount of cpu resources allowed','/ubuntu/spec/template/spec/containers/resources/limits/cpu','2','1','number',6),
	 (7,'Mount path for 1 volume','Path within the container at which the volume should be mounted. Must not contain ":".','/ubuntu/spec/template/spec/containers/volumeMounts[@n="1"]/mountPath','/home/sdl/workspace','/home/sdl/workspace','text',6);
