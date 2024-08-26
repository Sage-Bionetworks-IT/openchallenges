import aws_cdk as cdk

from openchallenges.bucket_stack import BucketStack
from openchallenges.network_stack import NetworkStack
from openchallenges.ecs_stack import EcsStack
from openchallenges.service_stack import ServiceStack
from openchallenges.service_stack import LoadBalancedServiceStack
from openchallenges.load_balancer_stack import LoadBalancerStack
from openchallenges.service_props import ServiceProps
import openchallenges.utils as utils

app = cdk.App()

environment = utils.get_environment()
env_vars = app.node.try_get_context(environment)
secrets = utils.get_secrets(app)

bucket_stack = BucketStack(app, "openchallenges-buckets")
network_stack = NetworkStack(app, "openchallenges-network", env_vars["VPC_CIDR"])
ecs_stack = EcsStack(
    app, "openchallenges-ecs", network_stack.vpc, env_vars["DNS_NAMESPACE"]
)

mariadb_props = ServiceProps(
    "openchallenges-mariadb",
    3306,
    512,
    "ghcr.io/sage-bionetworks/openchallenges-mariadb:edge",
    # "docker/mariadb",
    {
        "MARIADB_USER": "maria",
        "MARIADB_PASSWORD": secrets["MARIADB_PASSWORD"],
        "MARIADB_ROOT_PASSWORD": secrets["MARIADB_ROOT_PASSWORD"],
    },
)

mariadb_stack = ServiceStack(
    app, "openchallenges-mariadb", network_stack.vpc, ecs_stack.cluster, mariadb_props
)

elasticsearch_props = ServiceProps(
    "openchallenges-elasticsearch",
    9200,
    2048,
    "ghcr.io/sage-bionetworks/openchallenges-elasticsearch:edge",
    {
        # "node.name":"openchallenges-elasticsearch",
        # "cluster.name":"openchallenges-elasticsearch",
        # "discovery.seed_hosts=":"openchallenges-elasticsearch-node-2,openchallenges-elasticsearch-node-3",
        # "cluster.initial_master_nodes":"openchallenges-elasticsearch,openchallenges-elasticsearch-node-2,openchallenges-elasticsearch-node-3",
        "bootstrap.memory_lock": "true",
        # "ES_JAVA_OPTS":"-Xms1g -Xmx1g",
        "discovery.type": "single-node",  # https://stackoverflow.com/a/68253868
        "JAVA_TOOL_OPTIONS": "-XX:InitialHeapSize=1g -XX:MaxHeapSize=1g",
    },
)

elasticsearch_stack = ServiceStack(
    app,
    "openchallenges-elasticsearch",
    network_stack.vpc,
    ecs_stack.cluster,
    elasticsearch_props,
)

thumbor_props = ServiceProps(
    "openchallenges-thumbor",
    8889,
    512,
    "ghcr.io/sage-bionetworks/openchallenges-thumbor:edge",
    {
        "LOG_LEVEL": "info",
        "PORT": "8889",
        "LOADER": "thumbor_aws.loader",
        "AWS_LOADER_REGION_NAME": "us-east-1",
        "AWS_LOADER_BUCKET_NAME": bucket_stack.openchallenges_img_bucket.bucket_name,
        "AWS_LOADER_S3_ACCESS_KEY_ID": secrets["AWS_LOADER_S3_ACCESS_KEY_ID"],
        "AWS_LOADER_S3_SECRET_ACCESS_KEY": secrets["AWS_LOADER_S3_SECRET_ACCESS_KEY"],
        "AWS_LOADER_S3_ENDPOINT_URL": "http://s3.us-east-1.amazonaws.com",
        "AWS_LOADER_ROOT_PATH": "img",
        "STORAGE": "thumbor.storages.file_storage",
        "FILE_STORAGE_ROOT_PATH": "/data/storage",
        "RESULT_STORAGE": "thumbor.result_storages.file_storage",
        "RESULT_STORAGE_FILE_STORAGE_ROOT_PATH": "/data/result_storage",
        "RESULT_STORAGE_STORES_UNSAFE": "True",
        "RESULT_STORAGE_EXPIRATION_SECONDS": "2629746",
        "SECURITY_KEY": secrets["SECURITY_KEY"],
        "ALLOW_UNSAFE_URL": "True",
        "QUALITY": "100",
        "MAX_AGE": "86400",
        "AUTO_PNG_TO_JPG": "True",
        "HTTP_LOADER_VALIDATE_CERTS": "False",
    },
)

thumbor_stack = ServiceStack(
    app, "openchallenges-thumbor", network_stack.vpc, ecs_stack.cluster, thumbor_props
)

config_server_props = ServiceProps(
    "openchallenges-config-server",
    8090,
    1024,
    "ghcr.io/sage-bionetworks/openchallenges-config-server:edge",
    {
        "GIT_DEFAULT_LABEL": "test-2",
        "GIT_HOST_KEY_ALGORITHM": "ssh-ed25519",
        "GIT_HOST_KEY": secrets["GIT_HOST_KEY"],
        "GIT_PRIVATE_KEY": secrets["GIT_PRIVATE_KEY"],
        "GIT_URI": "git@github.com:Sage-Bionetworks/openchallenges-config-server-repository.git",
        "SERVER_PORT": "8090",
    },
)

config_server_stack = ServiceStack(
    app,
    "openchallenges-config-server",
    network_stack.vpc,
    ecs_stack.cluster,
    config_server_props,
)

service_registry_props = ServiceProps(
    "openchallenges-service-registry",
    8081,
    1024,
    "ghcr.io/sage-bionetworks/openchallenges-service-registry:edge",
    {
        "SERVER_PORT": "8081",
        "DEFAULT_ZONE": "http://localhost:8081/eureka",
        "SPRING_CLOUD_CONFIG_URI": "http://openchallenges-config-server:8090",
    },
)

service_registry_stack = ServiceStack(
    app,
    "openchallenges-service-registry",
    network_stack.vpc,
    ecs_stack.cluster,
    service_registry_props,
)
service_registry_stack.add_dependency(config_server_stack)

zipkin_props = ServiceProps(
    "openchallenges-zipkin",
    9411,
    512,
    "ghcr.io/sage-bionetworks/openchallenges-zipkin:edge",
    {},
)

zipkin_stack = ServiceStack(
    app, "openchallenges-zipkin", network_stack.vpc, ecs_stack.cluster, zipkin_props
)

image_service_props = ServiceProps(
    "openchallenges-image-service",
    8086,
    1024,
    "ghcr.io/sage-bionetworks/openchallenges-image-service:edge",
    {
        "SERVER_PORT": "8086",
        "SPRING_CLOUD_CONFIG_URI": "http://openchallenges-config-server:8090",
        "SERVICE_REGISTRY_URL": "http://openchallenges-service-registry:8081/eureka",
        "OPENCHALLENGES_IMAGE_SERVICE_IS_DEPLOYED_ON_AWS": "true",
    },
)

image_service_stack = ServiceStack(
    app,
    "openchallenges-image-service",
    network_stack.vpc,
    ecs_stack.cluster,
    image_service_props,
)
image_service_stack.add_dependency(service_registry_stack)
image_service_stack.add_dependency(thumbor_stack)
image_service_stack.add_dependency(zipkin_stack)

challenge_service_props = ServiceProps(
    "openchallenges-challenge-service",
    8085,
    1024,
    "ghcr.io/sage-bionetworks/openchallenges-challenge-service:edge",
    {
        "SERVER_PORT": "8085",
        "SPRING_CLOUD_CONFIG_URI": "http://openchallenges-config-server:8090",
        "SERVICE_REGISTRY_URL": "http://openchallenges-service-registry:8081/eureka",
        "KEYCLOAK_URL": "http://openchallenges-keycloak:8080",
        "SPRING_DATASOURCE_USERNAME": "maria",
        "SPRING_DATASOURCE_PASSWORD": secrets["MARIADB_PASSWORD"],
        "DB_URL": "jdbc:mysql://openchallenges-mariadb:3306/challenge_service?allowLoadLocalInfile=true",
        "DB_PLATFORMS_CSV_PATH": "/workspace/BOOT-INF/classes/db/platforms.csv",
        "DB_CHALLENGES_CSV_PATH": "/workspace/BOOT-INF/classes/db/challenges.csv",
        "DB_CONTRIBUTION_ROLES_CSV_PATH": "/workspace/BOOT-INF/classes/db/contribution_roles.csv",
        "DB_INCENTIVES_CSV_PATH": "/workspace/BOOT-INF/classes/db/incentives.csv",
        "DB_INPUT_DATA_TYPE_CSV_PATH": "/workspace/BOOT-INF/classes/db/input_data_type.csv",
        "DB_SUBMISSION_TYPES_CSV_PATH": "/workspace/BOOT-INF/classes/db/submission_types.csv",
        "DB_CATEGORIES_CSV_PATH": "/workspace/BOOT-INF/classes/db/categories.csv",
        "DB_EDAM_CONCEPT_CSV_PATH": "/workspace/BOOT-INF/classes/db/edam_concept.csv",
        "OPENCHALLENGES_CHALLENGE_SERVICE_IS_DEPLOYED_ON_AWS": "true",
    },
)

challenge_service_stack = ServiceStack(
    app,
    "openchallenges-challenge-service",
    network_stack.vpc,
    ecs_stack.cluster,
    challenge_service_props,
)
challenge_service_stack.add_dependency(service_registry_stack)
challenge_service_stack.add_dependency(mariadb_stack)
challenge_service_stack.add_dependency(elasticsearch_stack)
challenge_service_stack.add_dependency(zipkin_stack)


organization_service_props = ServiceProps(
    "openchallenges-organization-service",
    8084,
    1024,
    "ghcr.io/sage-bionetworks/openchallenges-organization-service:edge",
    {
        "SERVER_PORT": "8084",
        "SPRING_CLOUD_CONFIG_URI": "http://openchallenges-config-server:8090",
        "KEYCLOAK_URL": "http://openchallenges-keycloak:8080",
        "SERVICE_REGISTRY_URL": "http://openchallenges-service-registry:8081/eureka",
        "SPRING_DATASOURCE_USERNAME": "maria",
        "SPRING_DATASOURCE_PASSWORD": secrets["MARIADB_PASSWORD"],
        "DB_URL": "jdbc:mysql://openchallenges-mariadb:3306/organization_service?allowLoadLocalInfile=true",
        "DB_ORGANIZATIONS_CSV_PATH": "/workspace/BOOT-INF/classes/db/organizations.csv",
        "DB_CONTRIBUTION_ROLES_CSV_PATH": "/workspace/BOOT-INF/classes/db/contribution_roles.csv",
        "OPENCHALLENGES_ORGANIZATION_SERVICE_IS_DEPLOYED_ON_AWS": "true",
    },
)

organization_service_stack = ServiceStack(
    app,
    "openchallenges-organization-service",
    network_stack.vpc,
    ecs_stack.cluster,
    organization_service_props,
)
organization_service_stack.add_dependency(image_service_stack)
organization_service_stack.add_dependency(mariadb_stack)
organization_service_stack.add_dependency(elasticsearch_stack)
organization_service_stack.add_dependency(zipkin_stack)

api_gateway_props = ServiceProps(
    "openchallenges-api-gateway",
    8082,
    1024,
    "ghcr.io/sage-bionetworks/openchallenges-api-gateway:edge",
    {
        "SERVER_PORT": "8082",
        "SPRING_CLOUD_CONFIG_URI": "http://openchallenges-config-server:8090",
        "SERVICE_REGISTRY_URL": "http://openchallenges-service-registry:8081/eureka",
        "KEYCLOAK_URL": "http://openchallenges-keycloak:8080",
        "OPENCHALLENGES_API_GATEWAY_IS_DEPLOYED_ON_AWS": "true",
    },
)

api_gateway_stack = ServiceStack(
    app,
    "openchallenges-api-gateway",
    network_stack.vpc,
    ecs_stack.cluster,
    api_gateway_props,
)
api_gateway_stack.add_dependency(service_registry_stack)

oc_app_props = ServiceProps(
    "openchallenges-app",
    4200,
    1024,
    "ghcr.io/sage-bionetworks/openchallenges-app:edge",
    {
        "API_DOCS_URL": "http://openchallenges-api-docs:8010/api-docs",
        "APP_VERSION": "1.0.0-alpha",
        "CSR_API_URL": "http://openchallenges-api-gateway:8082/api/v1",
        "DATA_UPDATED_ON": "2023-09-26",
        "ENVIRONMENT": "production",
        "GOOGLE_TAG_MANAGER_ID": "",
        "SSR_API_URL": "http://openchallenges-api-gateway:8082/api/v1",
    },
)

oc_app_stack = ServiceStack(
    app, "openchallenges-app", network_stack.vpc, ecs_stack.cluster, oc_app_props
)
oc_app_stack.add_dependency(organization_service_stack)
oc_app_stack.add_dependency(api_gateway_stack)
oc_app_stack.add_dependency(challenge_service_stack)
oc_app_stack.add_dependency(image_service_stack)

# From AWS docs https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect-concepts-deploy.html
# The public discovery and reachability should be created last by AWS CloudFormation, including the frontend
# client service. The services need to be created in this order to prevent an time period when the frontend
# client service is running and available the public, but a backend isn't.
load_balancer_stack = LoadBalancerStack(
    app, "openchallenges-load-balancer", network_stack.vpc
)

api_docs_props = ServiceProps(
    "openchallenges-api-docs",
    8010,
    256,
    "ghcr.io/sage-bionetworks/openchallenges-api-docs:edge",
    {"PORT": "8010"},
)
api_docs_stack = LoadBalancedServiceStack(
    app,
    "openchallenges-api-docs",
    network_stack.vpc,
    ecs_stack.cluster,
    api_docs_props,
    load_balancer_stack.alb,
    8010,
    health_check_interval=5,
)

apex_service_props = ServiceProps(
    "openchallenges-apex",
    8000,
    200,
    "ghcr.io/sage-bionetworks/openchallenges-apex:edge",
    {
        "API_DOCS_HOST": "openchallenges-api-docs",
        "API_DOCS_PORT": "8010",
        "API_GATEWAY_HOST": "openchallenges-api-gateway",
        "API_GATEWAY_PORT": "8082",
        "APP_HOST": "openchallenges-app",
        "APP_PORT": "4200",
        "THUMBOR_HOST": "openchallenges-thumbor",
        "THUMBOR_PORT": "8889",
        "ZIPKIN_HOST": "openchallenges-zipkin",
        "ZIPKIN_PORT": "9411",
    },
)

apex_service_stack = LoadBalancedServiceStack(
    app,
    "openchallenges-apex",
    network_stack.vpc,
    ecs_stack.cluster,
    apex_service_props,
    load_balancer_stack.alb,
    80,
    "/health",
    5,
)
apex_service_stack.add_dependency(oc_app_stack)
apex_service_stack.add_dependency(api_docs_stack)


app.synth()
