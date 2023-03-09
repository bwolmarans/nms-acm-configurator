import yaml
import json

o_data=\
        {\
    "_links": [\
        {\
            "href": "/api/acm/v1/infrastructure/workspaces/team-sentence/environments/sentence-env",\
            "rel": "SELF"\
        }\
    ],\
    "id": 3,\
    "functions": [\
        "DEVPORTAL",\
        "API-GATEWAY"\
    ],\
    "metadata": {\
        "kind": "environment",\
        "link": {\
            "rel": "/api/acm/v1/infrastructure/workspaces/team-sentence/environments/sentence-env"\
        },\
        "ref": "/api/acm/v1/infrastructure/workspaces/team-sentence",\
        "tags": []\
    },\
    "name": "sentence-env",\
    "proxies": [\
        {\
            "backends": [\
                {\
                    "enableSRVRecordLookUp": 'false',\
                    "serviceContextRoot": "/",\
                    "serviceName": "portalapi-svc",\
                    "serviceTargets": [\
                        {\
                            "hostname": "127.0.0.1",\
                            "listener": {\
                                "enableTLS": 'false',\
                                "port": 8080,\
                                "transportProtocol": "HTTP"\
                            },\
                            "maxConnections": 0,\
                            "maxFails": 0\
                        }\
                    ]\
                }\
            ],\
            "configs": [\
                {\
                    "proxyConfig": {\
                        "backends": [\
                            {\
                                "enableSRVRecordLookUp": 'false',\
                                "serviceContextRoot": "/",\
                                "serviceName": "portalapi-svc",\
                                "serviceTargets": [\
                                    {\
                                        "hostname": "127.0.0.1",\
                                        "listener": {\
                                            "enableTLS": 'false',\
                                            "port": 8080,\
                                            "transportProtocol": "HTTP"\
                                        },\
                                        "maxConnections": 0,\
                                        "maxFails": 0\
                                    }\
                                ]\
                            }\
                        ],\
                        "hostname": "dev.sentence.com"\
                    }\
                }\
            ],\
            "hostnames": [\
                "dev.sentence.com"\
            ],\
            "listeners": [\
                {\
                    "ipv6": 'false',\
                    "port": 80,\
                    "tlsEnabled": 'false',\
                    "transportProtocol": "HTTP"\
                }\
            ],\
            "onboardingCommands": [\
                "curl -k https://\\u003cCTRL-FQDN\\u003e/install/nginx-agent \\u003e install.sh \\u0026\\u0026 sudo sh install.sh -g devportal-cluster \\u0026\\u0026 sudo systemctl start nginx-agent",\
                "wget https://\\u003cCTRL-FQDN\\u003e/install/nginx-agent --no-check-certificate -O install.sh \\u0026\\u0026 sudo sh install.sh -g devportal-cluster \\u0026\\u0026 sudo systemctl start nginx-agent"\
            ],\
            "policies": {\
                "proxy-response-headers": [\
                    {\
                        "action": {\
                            "config": [\
                                {\
                                    "always": 'false',\
                                    "enabled": 'true',\
                                    "name": "hide-nginx-headers"\
                                }\
                            ],\
                            "customResponseHeaders": [\
                                {\
                                    "always": 'false',\
                                    "key": "Cache-Control",\
                                    "value": "max-age=1d, must-revalidate"\
                                }\
                            ]\
                        },\
                        "metadata": {\
                            "labels": {\
                                "targetPolicyName": "default"\
                            }\
                        },\
                        "systemMetadata": {\
                            "appliedOn": "inbound",\
                            "context": "global"\
                        }\
                    }\
                ],\
                "rate-limit": [\
                    {\
                        "action": {\
                            "grpcStatusCode": 14,\
                            "limits": [\
                                {\
                                    "rate": "50r/s",\
                                    "rateLimitBy": "client.ip",\
                                    "throttle": {\
                                        "burst": 20,\
                                        "noDelay": 'true'\
                                    },\
                                    "zoneSize": "10M"\
                                }\
                            ],\
                            "returnCode": 429\
                        },\
                        "metadata": {\
                            "labels": {\
                                "targetPolicyName": "default"\
                            }\
                        },\
                        "systemMetadata": {\
                            "appliedOn": "inbound",\
                            "context": "global"\
                        }\
                    }\
                ]\
            },\
            "proxyClusterName": "devportal-cluster",\
            "runtime": "PORTAL-PROXY"\
        },\
        {\
            "hostnames": [\
                "api.sentence.com"\
            ],\
            "listeners": [\
                {\
                    "ipv6": 'false',\
                    "port": 80,\
                    "tlsEnabled": 'false',\
                    "transportProtocol": "HTTP"\
                }\
            ],\
            "onboardingCommands": [\
                "curl -k https://\\u003cCTRL-FQDN\\u003e/install/nginx-agent \\u003e install.sh \\u0026\\u0026 sudo sh install.sh -g api-cluster \\u0026\\u0026 sudo systemctl start nginx-agent",\
                "wget https://\\u003cCTRL-FQDN\\u003e/install/nginx-agent --no-check-certificate -O install.sh \\u0026\\u0026 sudo sh install.sh -g api-cluster \\u0026\\u0026 sudo systemctl start nginx-agent"\
            ],\
            "policies": {\
                "error-response-format": [\
                    {\
                        "action": {\
                            "400": {\
                                "errorCode": "400",\
                                "errorMessage": "Bad Request",\
                                "grpcStatusCode": 13\
                            },\
                            "401": {\
                                "errorCode": "401",\
                                "errorMessage": "Unauthorized",\
                                "grpcStatusCode": 16\
                            },\
                            "402": {\
                                "errorCode": "402",\
                                "errorMessage": "Payment Required",\
                                "grpcStatusCode": 14\
                            },\
                            "403": {\
                                "errorCode": "403",\
                                "errorMessage": "Forbidden",\
                                "grpcStatusCode": 7\
                            },\
                            "404": {\
                                "errorCode": "404",\
                                "errorMessage": "Not Found",\
                                "grpcStatusCode": 12\
                            },\
                            "405": {\
                                "errorCode": "405",\
                                "errorMessage": "Method Not Allowed",\
                                "grpcStatusCode": 13\
                            },\
                            "408": {\
                                "errorCode": "408",\
                                "errorMessage": "Request Timeout",\
                                "grpcStatusCode": 4\
                            },\
                            "413": {\
                                "errorCode": "413",\
                                "errorMessage": "Request Entity Too Large",\
                                "grpcStatusCode": 8\
                            },\
                            "414": {\
                                "errorCode": "414",\
                                "errorMessage": "Request URI Too Long",\
                                "grpcStatusCode": 8\
                            },\
                            "415": {\
                                "errorCode": "415",\
                                "errorMessage": "Unsupported Media Type",\
                                "grpcStatusCode": 13\
                            },\
                            "426": {\
                                "errorCode": "426",\
                                "errorMessage": "Upgrade Required",\
                                "grpcStatusCode": 13\
                            },\
                            "429": {\
                                "errorCode": "429",\
                                "errorMessage": "Too Many Requests",\
                                "grpcStatusCode": 14\
                            },\
                            "500": {\
                                "errorCode": "500",\
                                "errorMessage": "Internal Server Error",\
                                "grpcStatusCode": 13\
                            },\
                            "501": {\
                                "errorCode": "501",\
                                "errorMessage": "Not Implemented",\
                                "grpcStatusCode": 12\
                            },\
                            "502": {\
                                "errorCode": "502",\
                                "errorMessage": "Bad Gateway",\
                                "grpcStatusCode": 14\
                            },\
                            "503": {\
                                "errorCode": "503",\
                                "errorMessage": "Service Unavailable",\
                                "grpcStatusCode": 14\
                            },\
                            "504": {\
                                "errorCode": "504",\
                                "errorMessage": "Gateway Timeout",\
                                "grpcStatusCode": 14\
                            },\
                            "511": {\
                                "errorCode": "511",\
                                "errorMessage": "Network Authentication Required",\
                                "grpcStatusCode": 14\
                            }\
                        },\
                        "metadata": {\
                            "labels": {\
                                "targetPolicyName": "default"\
                            }\
                        },\
                        "systemMetadata": {\
                            "appliedOn": "outbound",\
                            "context": "global"\
                        }\
                    }\
                ],\
                "log-format": [\
                    {\
                        "action": {\
                            "enablePrettyPrint": 'false',\
                            "errorLogSeverity": "WARN",\
                            "logDestination": {\
                                "accessLogFileLocation": "/var/log/nginx/",\
                                "errorLogFileLocation": "/var/log/nginx/",\
                                "type": "FILE"\
                            },\
                            "logFormat": {\
                                "include": [\
                                    "BASIC",\
                                    "INGRESS",\
                                    "BACKEND",\
                                    "RESPONSE"\
                                ],\
                                "variables": []\
                            },\
                            "type": "JSON"\
                        },\
                        "metadata": {\
                            "labels": {\
                                "targetPolicyName": "default"\
                            }\
                        },\
                        "systemMetadata": {\
                            "appliedOn": "outbound",\
                            "context": "global"\
                        }\
                    }\
                ],\
                "proxy-response-headers": [\
                    {\
                        "action": {\
                            "config": [\
                                {\
                                    "always": 'true',\
                                    "enabled": 'true',\
                                    "name": "web-security-headers"\
                                },\
                                {\
                                    "always": 'true',\
                                    "enabled": 'true',\
                                    "name": "correlation-id"\
                                },\
                                {\
                                    "always": 'false',\
                                    "enabled": 'true',\
                                    "name": "latency-headers"\
                                },\
                                {\
                                    "always": 'true',\
                                    "enabled": 'true',\
                                    "name": "cache-headers"\
                                },\
                                {\
                                    "always": 'false',\
                                    "enabled": 'false',\
                                    "name": "hide-nginx-headers"\
                                },\
                                {\
                                    "always": 'true',\
                                    "enabled": 'true',\
                                    "name": "client-headers"\
                                }\
                            ]\
                        },\
                        "metadata": {\
                            "labels": {\
                                "targetPolicyName": "default"\
                            }\
                        },\
                        "systemMetadata": {\
                            "appliedOn": "inbound",\
                            "context": "global"\
                        }\
                    }\
                ],\
                "request-body-size-limit": [\
                    {\
                        "action": {\
                            "grpcStatusCode": 8,\
                            "returnCode": 413,\
                            "size": "1M"\
                        },\
                        "metadata": {\
                            "labels": {\
                                "targetPolicyName": "default"\
                            }\
                        },\
                        "systemMetadata": {\
                            "appliedOn": "inbound",\
                            "context": "global"\
                        }\
                    }\
                ],\
                "request-correlation-id": [\
                    {\
                        "action": {\
                            "httpHeaderName": "x-correlation-id"\
                        },\
                        "metadata": {\
                            "labels": {\
                                "targetPolicyName": "default"\
                            }\
                        },\
                        "systemMetadata": {\
                            "appliedOn": "inbound",\
                            "context": "global"\
                        }\
                    }\
                ]\
            },\
            "proxyClusterName": "api-cluster",\
            "runtime": "GATEWAY-PROXY"\
        },\
        {\
            "hostnames": [\
                "acm.dev.sentence.com"\
            ],\
            "listeners": [\
                {\
                    "ipv6": 'false',\
                    "port": 81,\
                    "tlsEnabled": 'false',\
                    "transportProtocol": "HTTP"\
                }\
            ],\
            "onboardingCommands": [\
                "curl -k https://\\u003cCTRL-FQDN\\u003e/install/nginx-agent \\u003e install.sh \\u0026\\u0026 sudo sh install.sh -g devportal-cluster \\u0026\\u0026 sudo systemctl start nginx-agent",\
                "wget https://\\u003cCTRL-FQDN\\u003e/install/nginx-agent --no-check-certificate -O install.sh \\u0026\\u0026 sudo sh install.sh -g devportal-cluster \\u0026\\u0026 sudo systemctl start nginx-agent"\
            ],\
            "policies": {\
                "proxy-response-headers": [\
                    {\
                        "action": {\
                            "config": [\
                                {\
                                    "always": 'false',\
                                    "enabled": 'true',\
                                    "name": "hide-nginx-headers"\
                                }\
                            ]\
                        },\
                        "metadata": {\
                            "labels": {\
                                "targetPolicyName": "default"\
                            }\
                        },\
                        "systemMetadata": {\
                            "appliedOn": "inbound",\
                            "context": "global"\
                        }\
                    }\
                ],\
                "rate-limit": [\
                    {\
                        "action": {\
                            "grpcStatusCode": 14,\
                            "limits": [\
                                {\
                                    "rate": "100r/s",\
                                    "rateLimitBy": "client.ip",\
                                    "throttle": {\
                                        "burst": 20,\
                                        "noDelay": 'true'\
                                    },\
                                    "zoneSize": "10M"\
                                }\
                            ],\
                            "returnCode": 429\
                        },\
                        "metadata": {\
                            "labels": {\
                                "targetPolicyName": "default"\
                            }\
                        },\
                        "systemMetadata": {\
                            "appliedOn": "inbound",\
                            "context": "global"\
                        }\
                    }\
                ]\
            },\
            "proxyClusterName": "devportal-cluster",\
            "runtime": "INT-PORTAL-ACM-PROXY"\
        }\
    ],\
    "systemProperties": {\
        "acmHostName": "10.1.1.6"\
    },\
    "type": "NON-PROD"\
}\



pkce_policy={ "oidc-authz": [ { "metadata": { "labels": { "targetPolicyName": "default" } }, "systemMetadata": { "appliedOn": "inbound", "context": "global" }, "action": { "authFlowType": "PKCE", "authorizationEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/auth", "errorReturnConditions": { "noMatch": { "returnCode": 403 }, "notSupplied": { "returnCode": 401 } }, "forwardTokenToBackend": "access_token", "jwksURI": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/certs", "logOffEndpoint": " http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/logout", "returnTokenToClientOnLogin": "none", "tokenEndpoint": " http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/token", "uris": { "loginURI": "/login", "logoutURI": "/logout", "redirectURI": "/_codexch", "userInfoURI": "/userinfo" }, "userInfoEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/userinfo" }, "data": [ { "appName": "devportal", "clientID": "devportal", "scopes": "openid", "source": "ACM" } ] } ] }

data = [ { 'a':'A', 'b':(2, 4), 'c':3.0, "enableSRVRecordLookUp":'false' } ]
print(data[0]['b'])
print(data)
del data[0]['c']
print(data)
quit()
print(pkce_policy['oidc-authz'][0]['action']['tokenEndpoint'])
print(o_data['proxies'][0]['hostnames'])
print(o_data['proxies'][0]['policies'])
o_data['proxies'][0]['policies']['oidc-authz']=[ { "metadata": { "labels": { "targetPolicyName": "default" } }, "systemMetadata": { "appliedOn": "inbound", "context": "global" }, "action": { "authFlowType": "PKCE", "authorizationEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/auth", "errorReturnConditions": { "noMatch": { "returnCode": 403 }, "notSupplied": { "returnCode": 401 } }, "forwardTokenToBackend": "access_token", "jwksURI": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/certs", "logOffEndpoint": " http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/logout", "returnTokenToClientOnLogin": "none", "tokenEndpoint": " http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/token", "uris": { "loginURI": "/login", "logoutURI": "/logout", "redirectURI": "/_codexch", "userInfoURI": "/userinfo" }, "userInfoEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/userinfo" }, "data": [ { "appName": "devportal", "clientID": "devportal", "scopes": "openid", "source": "ACM" } ] } ]
print("")
print(o_data['proxies'][0]['policies'])
print("")
print("")
print("")
print(o_data)


