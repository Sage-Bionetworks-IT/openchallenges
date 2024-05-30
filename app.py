#!/usr/bin/env python3
import os

import aws_cdk as cdk
from jproperties import Properties

from openchallenges.bucket_stack import BucketStack
from openchallenges.network_stack import NetworkStack
from openchallenges.ecs_stack import EcsStack
from openchallenges.app_stack import AppStack
from openchallenges.service_props import ServiceProps

# get configs from file
configs = Properties()
with open('.openchallenges', 'rb') as config_file:
  configs.load(config_file)

app = cdk.App()

bucket_stack = BucketStack(app, "OpenChallengesBuckets")
network_stack = NetworkStack(app, "OpenChallengesNetwork")
ecs_stack = EcsStack(app, "OpenChallengesEcs", network_stack.vpc)

zipkin_props = ServiceProps(ecs_stack.cluster, network_stack.http_listener, ecs_stack.service_map,
                        "zipkin",
                        9411,
                        512,
                        "ghcr.io/sage-bionetworks/openchallenges-zipkin:sha-a1c076d",
                        {},
                        "",False,"/zipkin/",10)

AppStack(app, "OpenChallengesZipkin", zipkin_props)

mariadb_props = ServiceProps(ecs_stack.cluster, network_stack.http_listener, ecs_stack.service_map,
                        "mariadb",
                        3306,
                        512,
                        "ghcr.io/sage-bionetworks/openchallenges-mariadb:sha-8a48c0f",
                        {
                                "MARIADB_USER":"maria",
                                "MARIADB_PASSWORD":configs.get("MARIADB_PASSWORD").data,
                                "MARIADB_ROOT_PASSWORD":configs.get("MARIADB_ROOT_PASSWORD").data
                         },
                        "openchallenges-mariadb",False,"",10)

AppStack(app, "OpenChallengesMariaDb", mariadb_props)

api_docs_props = ServiceProps(ecs_stack.cluster, network_stack.http_listener, ecs_stack.service_map,
                        "api-docs",
                        8010,
                        256,
                        "ghcr.io/sage-bionetworks/openchallenges-api-docs:sha-8a48c0f",
                        {
                                "PORT":"8010"
                         },
                        "",False,"",10)

AppStack(app, "OpenChallengesApidocs", api_docs_props)

config_server_props = ServiceProps(ecs_stack.cluster, network_stack.http_listener, ecs_stack.service_map,
                        "config-server",
                        8090,
                        1024,
                        "ghcr.io/sage-bionetworks/openchallenges-config-server:sha-8a48c0f",
                        {
                                     "GIT_DEFAULT_LABEL":"test-2",
                                     "GIT_HOST_KEY_ALGORITHM":"ssh-ed25519",
                                     "GIT_HOST_KEY":configs.get("GIT_HOST_KEY").data,
                                     "GIT_PRIVATE_KEY":configs.get("GIT_PRIVATE_KEY").data,
                                     "GIT_URI":"git@github.com:Sage-Bionetworks/openchallenges-config-server-repository.git",
                                     "SERVER_PORT":"8090"
                                   },
                        "/data/db",False, "", 10)

AppStack(app, "OpenChallengesConfigServer", config_server_props)


thumbor_props = ServiceProps(ecs_stack.cluster, network_stack.http_listener, ecs_stack.service_map,
                        "thumbor",
                        8889,
                        512,
                        "ghcr.io/sage-bionetworks/openchallenges-thumbor:sha-8a48c0f",
                        {
                                   "LOG_LEVEL":"info",
                                   "PORT":"8889",
                                   "LOADER":"thumbor_aws.loader",
                                   "AWS_LOADER_REGION_NAME":"us-east-1",
                                   "AWS_LOADER_BUCKET_NAME":bucket_stack.openchallenges_img_bucket.bucket_name,
                                   "AWS_LOADER_S3_ACCESS_KEY_ID":configs.get("AWS_LOADER_S3_ACCESS_KEY_ID").data,
                                   "AWS_LOADER_S3_SECRET_ACCESS_KEY":configs.get("AWS_LOADER_S3_SECRET_ACCESS_KEY").data,
                                   "AWS_LOADER_S3_ENDPOINT_URL":"http://s3.us-east-1.amazonaws.com",
                                    "AWS_LOADER_ROOT_PATH":"img",
                                    "STORAGE":"thumbor.storages.file_storage",
                                    "FILE_STORAGE_ROOT_PATH":"/data/storage",
                                    "RESULT_STORAGE":"thumbor.result_storages.file_storage",
                                    "RESULT_STORAGE_FILE_STORAGE_ROOT_PATH":"/data/result_storage",
                                    "RESULT_STORAGE_STORES_UNSAFE":"True",
                                    "RESULT_STORAGE_EXPIRATION_SECONDS":"2629746",
                                    "SECURITY_KEY":configs.get("SECURITY_KEY").data,
                                    "ALLOW_UNSAFE_URL":"True",
                                    "QUALITY":"100",
                                    "MAX_AGE":"86400",
                                    "AUTO_PNG_TO_JPG":"True",
                                    "HTTP_LOADER_VALIDATE_CERTS":"False"
                                  },
                        "/data",False, "", 10)

AppStack(app, "OpenChallengesThumbor", thumbor_props)


elasticache_props = ServiceProps(ecs_stack.cluster, network_stack.http_listener, ecs_stack.service_map,
                        "elasticache",
                        9200,
                        2048,
                        "ghcr.io/sage-bionetworks/openchallenges-elasticsearch:sha-8a48c0f",
                        {
                                   # "node.name":"openchallenges-elasticsearch",
                                   # "cluster.name":"openchallenges-elasticsearch",
                                   # "discovery.seed_hosts=":"openchallenges-elasticsearch-node-2,openchallenges-elasticsearch-node-3",
                                   # "cluster.initial_master_nodes":"openchallenges-elasticsearch,openchallenges-elasticsearch-node-2,openchallenges-elasticsearch-node-3",
                                   "bootstrap.memory_lock":"true",
                                   # "ES_JAVA_OPTS":"-Xms1g -Xmx1g",
                                   "discovery.type":"single-node",  # https://stackoverflow.com/a/68253868
                                   "JAVA_TOOL_OPTIONS":"-XX:InitialHeapSize=1g -XX:MaxHeapSize=1g"
                                  },
                        "",False, "", 10)

AppStack(app, "OpenChallengesElasticache", elasticache_props)

# service_registry_props = ServiceProps(ecs_stack.cluster, network_stack.http_listener, ecs_stack.service_map,
#                         "service_registry",
#                         8081,
#                         1024,
#                         "ghcr.io/sage-bionetworks/openchallenges-service-registry:sha-8a48c0f",
#                         {
#                                    "SERVER_PORT":"8081",
#                                    "DEFAULT_ZONE":"http://localhost:8081/eureka"
#                                   },
#                         "",False, "", 10)
#
# AppStack(app, "OpenChallengesServiceRegistry", service_registry_props)

app.synth()
