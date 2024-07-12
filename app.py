#!/usr/bin/env python3
import os

import aws_cdk as cdk
from jproperties import Properties

from openchallenges.bucket_stack import BucketStack
from openchallenges.network_stack import NetworkStack
from openchallenges.ecs_stack import EcsStack
from openchallenges.service_stack import ServiceStack
from openchallenges.service_stack import ExternalServiceStack
from openchallenges.load_balancer_stack import LoadBalancerStack
from openchallenges.service_props import ServiceProps

# get configs from file
configs = Properties()
with open('.openchallenges', 'rb') as config_file:
  configs.load(config_file)

DNS_NAMESPACE = "oc.org"
VPC_CIDR="10.255.91.0/24"

app = cdk.App()

bucket_stack = BucketStack(app, "OpenChallengesBuckets")
network_stack = NetworkStack(app, "OpenChallengesNetwork", VPC_CIDR)
ecs_stack = EcsStack(app, "OpenChallengesEcs", network_stack.vpc, DNS_NAMESPACE)
aws_api_gateway_stack = LoadBalancerStack(app, "OpenChallengesAwsApiGateway", network_stack.vpc)

elasticsearch_props = ServiceProps(
                        "elasticsearch",
                        9200,
                        2048,
                        "ghcr.io/sage-bionetworks/openchallenges-elasticsearch:edge",
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
                        )

elasticsearch_stack = ServiceStack(app, "OpenChallengesElasticsearch", network_stack.vpc, ecs_stack.cluster, elasticsearch_props)

thumbor_props = ServiceProps(
                        "thumbor",
                        8889,
                        512,
                        "ghcr.io/sage-bionetworks/openchallenges-thumbor:edge",
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
                        )

thumbor_stack = ServiceStack(app, "OpenChallengesThumbor", network_stack.vpc, ecs_stack.cluster, thumbor_props)

mariadb_props = ServiceProps(
                        "mariadb",
                        3306,
                        512,
                        "ghcr.io/sage-bionetworks/openchallenges-mariadb:edge",
                        #"docker/mariadb",
                        {
                                "MARIADB_USER":"maria",
                                "MARIADB_PASSWORD":configs.get("MARIADB_PASSWORD").data,
                                "MARIADB_ROOT_PASSWORD":configs.get("MARIADB_ROOT_PASSWORD").data
                         },
                        )

mariadb_stack = ServiceStack(app, "OpenChallengesMariaDb", network_stack.vpc, ecs_stack.cluster, mariadb_props)


api_docs_props = ServiceProps(
                        "api-docs",
                        8010,
                        256,
                        "ghcr.io/sage-bionetworks/openchallenges-api-docs:edge",
                        {
                                "PORT":"8010"
                         },
                        )

api_docs_stack = ServiceStack(app, "OpenChallengesApiDocs", network_stack.vpc, ecs_stack.cluster, api_docs_props)

zipkin_props = ServiceProps(
                        "zipkin",
                        9411,
                        512,
                        "ghcr.io/sage-bionetworks/openchallenges-zipkin:edge",
                        {},
                        )

zipkin_stack = ServiceStack(app, "OpenChallengesZipkin", network_stack.vpc, ecs_stack.cluster, zipkin_props)


config_server_props = ServiceProps(
                        "config-server",
                        8090,
                        1024,
                        "ghcr.io/sage-bionetworks/openchallenges-config-server:edge",
                        {
                                     "GIT_DEFAULT_LABEL":"khai-test",
                                     "GIT_HOST_KEY_ALGORITHM":"ssh-ed25519",
                                     "GIT_HOST_KEY":configs.get("GIT_HOST_KEY").data,
                                     "GIT_PRIVATE_KEY":configs.get("GIT_PRIVATE_KEY").data,
                                     "GIT_URI":"git@github.com:Sage-Bionetworks/openchallenges-config-server-repository.git",
                                     "SERVER_PORT":"8090"
                                   },
                        )

config_server_stack = ServiceStack(app, "OpenChallengesConfigServer", network_stack.vpc, ecs_stack.cluster, config_server_props)

service_registry_props = ServiceProps(
                        "service-registry",
                        8081,
                        1024,
                        "ghcr.io/sage-bionetworks/openchallenges-service-registry:edge",
                        {
                                   "SERVER_PORT":"8081",
                                   "DEFAULT_ZONE":"http://localhost:8081/eureka",
                                   "SPRING_CLOUD_CONFIG_URI":"http://config-server.oc.org:8090"
                                  },
                        )

service_registry_stack = ServiceStack(app, "OpenChallengesServiceRegistry", network_stack.vpc, ecs_stack.cluster, service_registry_props)
service_registry_stack.add_dependency(config_server_stack)

api_gateway_props = ServiceProps(
                        "api-gateway",
                        8082,
                        1024,
                        "ghcr.io/sage-bionetworks/openchallenges-api-gateway:edge",
                        {
                                   "SERVER_PORT":"8082",
                                   "SPRING_CLOUD_CONFIG_URI":"http://config-server.oc.org:8090",
                                   "SERVICE_REGISTRY_URL":"http://service-registry.oc.org:8081/eureka",
                                   "KEYCLOAK_URL":"http://openchallenges-keycloak:8080"
                                  },
                        )

api_gateway_stack = ServiceStack(app, "OpenChallengesApiGateway", network_stack.vpc, ecs_stack.cluster, api_gateway_props)
api_gateway_stack.add_dependency(service_registry_stack)

image_service_props = ServiceProps(
                        "image-service",
                        8086,
                        1024,
                        "ghcr.io/sage-bionetworks/openchallenges-image-service:edge",
                        {
                                  "SERVER_PORT":"8086",
                                  "SPRING_CLOUD_CONFIG_URI": "http://config-server.oc.org:8090",
                                  "SERVICE_REGISTRY_URL":"http://service-registry.oc.org:8081/eureka",
                                  },
                        )

image_service_stack = ServiceStack(app, "OpenChallengesImageService", network_stack.vpc, ecs_stack.cluster, image_service_props)
image_service_stack.add_dependency(service_registry_stack)
image_service_stack.add_dependency(thumbor_stack)
image_service_stack.add_dependency(zipkin_stack)


challenge_service_props = ServiceProps(
                        "challenge-service",
                        8085,
                        1024,
                        "ghcr.io/sage-bionetworks/openchallenges-challenge-service:edge",
                        {
                                   "SERVER_PORT":"8085",
                                   "SPRING_CLOUD_CONFIG_URI": "http://config-server.oc.org:8090",
                                   "SERVICE_REGISTRY_URL":"http://service-registry.oc.org:8081/eureka",
                                   "KEYCLOAK_URL":"http://openchallenges-keycloak:8080",
                                   "SPRING_DATASOURCE_USERNAME":"maria",
                                   "SPRING_DATASOURCE_PASSWORD":configs.get("MARIADB_PASSWORD").data,
                                   "DB_URL":"jdbc:mysql://mariadb.oc.org:3306/challenge_service?allowLoadLocalInfile=true",
                                    "DB_PLATFORMS_CSV_PATH":"/workspace/BOOT-INF/classes/db/platforms.csv",
                                    "DB_CHALLENGES_CSV_PATH":"/workspace/BOOT-INF/classes/db/challenges.csv",
                                    "DB_CONTRIBUTION_ROLES_CSV_PATH":"/workspace/BOOT-INF/classes/db/contribution_roles.csv",
                                    "DB_INCENTIVES_CSV_PATH":"/workspace/BOOT-INF/classes/db/incentives.csv",
                                    "DB_INPUT_DATA_TYPE_CSV_PATH":"/workspace/BOOT-INF/classes/db/input_data_type.csv",
                                    "DB_SUBMISSION_TYPES_CSV_PATH":"/workspace/BOOT-INF/classes/db/submission_types.csv",
                                    "DB_CATEGORIES_CSV_PATH":"/workspace/BOOT-INF/classes/db/categories.csv",
                                    "DB_EDAM_CONCEPT_CSV_PATH":"/workspace/BOOT-INF/classes/db/edam_concept.csv"
                                  },
                        )

challenge_service_stack = ServiceStack(app, "OpenChallengesChallengeService", network_stack.vpc, ecs_stack.cluster, challenge_service_props)
challenge_service_stack.add_dependency(service_registry_stack)
challenge_service_stack.add_dependency(mariadb_stack)
challenge_service_stack.add_dependency(elasticsearch_stack)
challenge_service_stack.add_dependency(zipkin_stack)


organization_service_props = ServiceProps(
                        "organization-service",
                        8084,
                        1024,
                        "ghcr.io/sage-bionetworks/openchallenges-organization-service:edge",
                        {
                                   "SERVER_PORT":"8084",
                                   "SPRING_CLOUD_CONFIG_URI": "http://config-server.oc.org:8090",
                                   "KEYCLOAK_URL":"http://openchallenges-keycloak:8080",
                                   "SERVICE_REGISTRY_URL":"http://service-registry.oc.org:8081/eureka",
                                    "SPRING_DATASOURCE_USERNAME": "maria",
                                    "SPRING_DATASOURCE_PASSWORD": configs.get("MARIADB_PASSWORD").data,
                                    "DB_URL":"jdbc:mysql://mariadb.oc.org:3306/organization_service?allowLoadLocalInfile=true",
                                    "DB_ORGANIZATIONS_CSV_PATH":"/workspace/BOOT-INF/classes/db/organizations.csv",
                                    "DB_CONTRIBUTION_ROLES_CSV_PATH":"/workspace/BOOT-INF/classes/db/contribution_roles.csv",
                                  },
                        )

organization_service_stack = ServiceStack(app, "OpenChallengesOrganizationService", network_stack.vpc, ecs_stack.cluster, organization_service_props)
organization_service_stack.add_dependency(image_service_stack)
organization_service_stack.add_dependency(mariadb_stack)
organization_service_stack.add_dependency(elasticsearch_stack)
organization_service_stack.add_dependency(zipkin_stack)

oc_app_props = ServiceProps(
                        "app",
                        4200,
                        1024,
                        "ghcr.io/sage-bionetworks/openchallenges-app:edge",
                        {
                                    "API_DOCS_URL":"http://api-docs.oc.org:8010/api-docs",
                                    "APP_VERSION":"1.0.0-alpha",
                                    "CSR_API_URL":"http://api-gateway.oc.org:8082/api/v1",
                                    "DATA_UPDATED_ON":"2023-09-26",
                                    "ENVIRONMENT":"production",
                                    "GOOGLE_TAG_MANAGER_ID":"",
                                    "SSR_API_URL":"http://api-gateway.oc.org:8082/api/v1"
                                  },
                        )

oc_app_stack = ServiceStack(app, "OpenChallengesApp", network_stack.vpc, ecs_stack.cluster, oc_app_props)
oc_app_stack.add_dependency(organization_service_stack)
oc_app_stack.add_dependency(api_gateway_stack)
oc_app_stack.add_dependency(challenge_service_stack)
oc_app_stack.add_dependency(image_service_stack)

apex_service_props = ServiceProps(
                        "apex",
                        8000,
                        200,
                        "ghcr.io/sage-bionetworks/openchallenges-apex:edge",
                        {
                                    "API_DOCS_HOST":"api-docs.oc.org",
                                    "API_DOCS_PORT":"8010",
                                    "API_GATEWAY_HOST":"api-gateway.oc.org",
                                    "API_GATEWAY_PORT":"8082",
                                    "APP_HOST":"app.oc.org",
                                    "APP_PORT":"4200",
                                    "THUMBOR_HOST":"thumbor.oc.org",
                                    "THUMBOR_PORT":"8889",
                                    "ZIPKIN_HOST":"zipkin.oc.org",
                                    "ZIPKIN_PORT":"9411"
                                  },
                        )

apex_service_stack = ExternalServiceStack(app, "OpenChallengesApex", network_stack.vpc, ecs_stack.cluster,
                                          apex_service_props, aws_api_gateway_stack.alb)
apex_service_stack.add_dependency(oc_app_stack)
apex_service_stack.add_dependency(api_docs_stack)


app.synth()
