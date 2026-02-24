# ================ STEP 1 ================
FROM node:16 AS builder 

WORKDIR /frontend

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build


# ================ STEP 2 ================
FROM nginx:latest

COPY --from=builder /frontend/build /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]