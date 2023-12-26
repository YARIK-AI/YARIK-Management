insert into etl.components 
values (1, 'PostgreSQL', 'The artifact storage component is a PostgreSQL database. Designed to store parameters of configuration files of YARIK platform components.'), (2, 'Ubuntu', 'Ubuntu operating system running inside a container');

insert into etl.files
values (1, 'Kubernetes deployment configuration', 'Describes the options for deploying a component in a Kubernetes cluster', 'postgres.yaml', 'yaml', 'utf-8', 'postgres/file/postgres.yaml', 'postgres/xslt/postgres.xml', 'postgres/xsd/postgres.xsd', 1),
(2, 'Kubernetes deployment configuration', 'Describes the options for deploying a component in a Kubernetes cluster', 'ubuntu.yaml', 'yaml', 'utf-8', 'ubuntu/file/ubuntu.yaml', 'ubuntu/xslt/ubuntu.xml', 'ubuntu/xsd/ubuntu.xsd', 2),
(3, 'Kubernetes service configuration', 'Describes the parameters of the service created in the Kubernetes cluster', 'service.yaml', 'yaml', 'utf-8', 'postgres/file/service.yaml', 'postgres/xslt/service.xml', 'postgres/xsd/service.xsd', 1);

insert into etl.parameters 
values (1, 'Container port', 'Number of port to expose on the pods IP address. This must be a valid port number, 0 < x < 65536.', '/postgres/spec/template/spec/containers/ports/containerPort', '5432', 1), 
(2, 'Number of replicas', 'This is the number of desired replicas. This is a pointer to distinguish between explicit zero and unspecified', '/postgres/spec/replicas', '1', 1),
(3, 'Required memory', 'Describes the minimum amount of ram required', '/ubuntu/spec/template/spec/containers/resources/requests/memory', '2Gi', 2), 
(4, 'Required cpu', 'Describes the minimum amount of cpu required', '/ubuntu/spec/template/spec/containers/resources/requests/cpu', '2', 2), 
(5, 'Max memory', 'Describes the maximum amount of ram resources allowed', '/ubuntu/spec/template/spec/containers/resources/limits/memory', '2Gi', 2), 
(6, 'Max cpu', 'Describes the maximum amount of cpu resources allowed', '/ubuntu/spec/template/spec/containers/resources/limits/cpu', '2', 2), 
(7, 'Mount path for 1 volume', 'Path within the container at which the volume should be mounted. Must not contain ":".', '/ubuntu/spec/template/spec/containers/volumeMounts[@n="1"]/mountPath', '/home/sdl/workspace', 2), 
(8, 'Name of 1 volume', 'This must match the Name of a Volume.', '/ubuntu/spec/template/spec/containers/volumeMounts[@n="1"]/name', 'ubuntu-data', 2),
(9, 'Readonly flag for 1 volume mount', 'Mounted read-only if true, read-write otherwise.', '/ubuntu/spec/template/spec/containers/volumeMounts[@n="1"]/readOnly', 'false', 2),
(10, 'Mount path for 2 volume', 'Path within the container at which the volume should be mounted. Must not contain ":".', '/ubuntu/spec/template/spec/containers/volumeMounts[@n="2"]/mountPath', '/home/sdl/weg', 2), 
(11, 'Name of 2 volume', 'This must match the Name of a Volume.', '/ubuntu/spec/template/spec/containers/volumeMounts[@n="2"]/name', 'ubuntu-weg', 2),
(12, 'Readonly flag for 2 volume mount', 'Mounted read-only if true, read-write otherwise.', '/ubuntu/spec/template/spec/containers/volumeMounts[@n="2"]/readOnly', 'false', 2),
(13, 'Target port', 'Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME.', '/postgres/spec/ports/targetPort', '5432', 3), 
(14, 'Node port', 'The port on each node on which this service is exposed when type is NodePort or LoadBalancer.', '/postgres/spec/ports/nodePort', '32321', 3), 
(15, 'Port', 'The port that will be exposed by this service.', '/postgres/spec/ports/port', '3239', 3);