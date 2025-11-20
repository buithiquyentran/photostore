# Build stage
FROM node:20 AS build

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

ARG VITE_KEYCLOAK_URL
ENV VITE_KEYCLOAK_URL=${VITE_KEYCLOAK_URL}

ARG VITE_KEYCLOAK_REALM
ENV VITE_KEYCLOAK_REALM=${VITE_KEYCLOAK_REALM}

ARG VITE_KEYCLOAK_CLIENT
ENV VITE_KEYCLOAK_CLIENT=${VITE_KEYCLOAK_CLIENT}

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Serve stage - dùng nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf


EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
