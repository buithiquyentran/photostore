import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
  url: "http://localhost:8080/",
  realm: "photostore_realm",
  clientId: "photostore_client",
});

export default keycloak;
