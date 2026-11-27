FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
RUN printf 'server {\n\
  listen 80;\n\
  resolver 8.8.8.8 1.1.1.1 valid=30s;\n\
  location / {\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    try_files $uri $uri/ /index.html;\n\
  }\n\
  location /api/ {\n\
    set $backend "https://aurafarming-backend-krwu.onrender.com";\n\
    proxy_pass $backend;\n\
    proxy_ssl_server_name on;\n\
    proxy_ssl_protocols TLSv1.2 TLSv1.3;\n\
    proxy_set_header Host aurafarming-backend-krwu.onrender.com;\n\
    proxy_set_header X-Real-IP $remote_addr;\n\
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
    proxy_set_header X-Forwarded-Proto https;\n\
    proxy_read_timeout 120s;\n\
  }\n\
}\n' > /etc/nginx/conf.d/default.conf
EXPOSE 80
